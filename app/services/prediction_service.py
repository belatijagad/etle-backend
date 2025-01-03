import base64
import requests
import json
import os
from uuid import UUID
from PIL import Image
from fastapi import HTTPException, status

from app.core.config import settings
from app.core.exceptions import ImageNotFoundException
from app.models.violation import Violation, ViolationCreate
from app.services.base_service import BaseService
from app.models.image import Image as DBImage
from app.models.prediction import BoundingBox, PredictionResult

class PredictionService(BaseService):
  def __init__(self):
    self.api_url = f'{settings.ROBOFLOW_MODEL_URL}?api_key={settings.ROBOFLOW_API_KEY}'
    self.cropped_dir = settings.CROPPED_IMAGES_DIR
    self.base_url = settings.BASE_URL or "http://localhost:8000"
    os.makedirs(self.cropped_dir, exist_ok=True)

  async def predict_image(self, image_id: UUID) -> dict:
    try:
      image = await self._get_image(image_id)
      predictions = await self._run_prediction(image.filepath)
      original_id = os.path.splitext(os.path.basename(image.filepath))[0]
      cropped_images = await self._process_detections(original_id, image.filepath, predictions)
      result = PredictionResult(image_id=original_id, predictions=predictions, cropped_images=cropped_images)
      await self._save_predictions(image_id, predictions)
      return self._create_prediction_response(result)
    except ImageNotFoundException as e:
      raise e
    except Exception as e:
      print(f'Error during prediction: {str(e)}')  # Debug print
      raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f'An error occurred during prediction: {str(e)}')
    
  async def _process_detections(self, image_id: str, image_path: str, predictions: list[BoundingBox]) -> list[str]:
    driver_boxes = [pred for pred in predictions if pred.class_name == 'driver']
    helmet_boxes = [pred for pred in predictions if pred.class_name == 'helmet']
    cropped_images = []

    print(f"Processing image: {image_path}")
    print(f"Found {len(driver_boxes)} drivers and {len(helmet_boxes)} helmets")

    try:
      with Image.open(image_path) as img:
        for i, driver in enumerate(driver_boxes):
          closest_helmet = None
          min_distance = float('inf')
          
          for helmet in helmet_boxes:
            distance = self._calculate_distance(driver.x, driver.y, helmet.x, helmet.y)
            if distance < min_distance and distance < 200:
              min_distance = distance
              closest_helmet = helmet

          if not closest_helmet:
            try:
              # Add padding to the bounding box
              padding = 50
              bbox = (
                driver.x - driver.width/2 - padding,
                driver.y - driver.height/2 - padding,
                driver.width + 2*padding,
                driver.height + 2*padding
              )
              
              filename = f'{image_id}_violation_{i}.jpeg'
              filepath = os.path.join(self.cropped_dir, filename)
              
              os.makedirs(self.cropped_dir, exist_ok=True)
              await self._crop_and_save(img, bbox, filepath)
              cropped_images.append(filepath)
              
              # Save violation in database
              await self._save_violation(filepath)
              print(f"Saved violation in database for image: {image_id}")
              
            except Exception as e:
              print(f"Error processing violation {i}: {str(e)}")
              import traceback
              print(traceback.format_exc())

    except Exception as e:
      print(f"Error processing image: {str(e)}")
      import traceback
      print(traceback.format_exc())

    return cropped_images

  async def _save_violation(self, cropped_path: str) -> None:
    try:
      filename = os.path.basename(cropped_path)
      url_path = f"{self.base_url}/cropped_images/{filename}"
      
      violation_data = ViolationCreate(
        type=1,
        image_url=url_path
      )
      
      with self.get_session() as session:
        violation = Violation.model_validate(violation_data)
        session.add(violation)
        session.commit()
        print(f"Saved violation: {violation.id} with URL: {url_path}")
    except Exception as e:
      print(f"Error saving violation: {str(e)}")
      import traceback
      print(traceback.format_exc())
      raise e


  def _create_prediction_response(self, result: PredictionResult) -> dict:
    return {
      'status': 'success',
      'image_id': result.image_id,
      'predictions': [pred.model_dump() for pred in result.predictions],
      'cropped_images': result.cropped_images,
      'message': f'Detected {len(result.predictions)} objects'
    }

  async def _get_image(self, image_id: UUID) -> DBImage:
    with self.get_session() as session:
      image = session.get(DBImage, image_id)
      if not image:
        raise ImageNotFoundException()
      return image

  async def _run_prediction(self, image_path: str) -> list[BoundingBox]:
    if not os.path.exists(image_path):
      raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Image file not found')
    with open(image_path, 'rb') as img_file:
      encoded_image = base64.b64encode(img_file.read()).decode('utf-8')

    headers = {'Content-Type': 'application/json'}
    response = requests.post(self.api_url, data=encoded_image, headers=headers)
      
    if response.status_code != 200:
      raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f'Roboflow API error: {response.text}')

    data = response.json()
    predictions = []
    for pred in data['predictions']:
      bbox = BoundingBox(
        x=pred['x'],
        y=pred['y'],
        width=pred['width'],
        height=pred['height'],
        confidence=pred['confidence'],
        class_name=pred['class']
      )
      predictions.append(bbox)

    return predictions

  def _calculate_distance(self, x1: float, y1: float, x2: float, y2: float) -> float:
    return ((x1 - x2) ** 2 + (y1 - y2) ** 2) ** 0.5

  async def _crop_and_save(self, image: Image.Image, bbox: tuple[float, float, float, float], filepath: str) -> None:
    try:
      x, y, width, height = bbox
      img_width, img_height = image.size
      
      # Ensure coordinates are within image bounds
      left = max(0, int(x))
      top = max(0, int(y))
      right = min(img_width, int(x + width))
      bottom = min(img_height, int(y + height))
      
      if left >= right or top >= bottom:
        print(f'Invalid crop coordinates: left={left}, top={top}, right={right}, bottom={bottom}')
        return
      
      cropped = image.crop((left, top, right, bottom))
      cropped.save(filepath)
      print(f'Successfully saved cropped image: {filepath}')
    except Exception as e:
      print(f'Error saving cropped image: {str(e)}')
      raise e

  async def _save_predictions(self, image_id: UUID, predictions: list[BoundingBox]) -> None:
    with self.get_session() as session:
      image = session.get(DBImage, image_id)
      if not image: 
        raise ImageNotFoundException()      
      predictions_data = [pred.model_dump() for pred in predictions]
      image.predictions = json.dumps(predictions_data)
      session.add(image)
      session.commit()