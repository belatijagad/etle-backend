from ultralytics import YOLO
from PIL import Image
import os
import json
from uuid import UUID
from fastapi import HTTPException, status
from sqlmodel import Session
from app.core.db import engine
from app.models.image import Image as DBImage

class PredictionService:
  def __init__(self, model_path: str = 'yolov8n.pt'):
    self._load_model(model_path)

  def _load_model(self, model_path: str) -> None:
    try:
      self.model = YOLO(model_path)
    except Exception as e:
      raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail=f'Failed to load YOLO model: {str(e)}'
      )

  async def predict_image(self, image_id: UUID) -> dict:
    try:
      image = await self._get_image(image_id)
      predictions = await self._run_prediction(image.filepath)
      await self._save_predictions(image_id, predictions)
      return {
          'status': 'success',
          'image_id': str(image_id),
          'predictions': predictions,
          'message': f'Detected {len(predictions)} objects'
      }
    except HTTPException as he:
      raise he
    except Exception as e:
      raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail=f'An error occurred during prediction: {str(e)}'
      )

  async def _get_image(self, image_id: UUID) -> DBImage:
    with Session(engine) as session:
      image = session.get(DBImage, image_id)
      if not image:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Image not found')
      return image

  async def _run_prediction(self, image_path: str) -> list:
    if not os.path.exists(image_path):
      raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail='Image file not found'
      )

    results = self.model(image_path)
    predictions = []
    
    for result in results:
      boxes = result.boxes
      for box in boxes:
        pred = {
          'class': result.names[int(box.cls[0])],
          'confidence': float(box.conf[0]),
          'bbox': box.xyxy[0].tolist()
        }
        predictions.append(pred)
            
    return predictions

  async def _save_predictions(self, image_id: UUID, predictions: list) -> None:
    with Session(engine) as session:
      image = session.get(DBImage, image_id)
      if not image:
        raise HTTPException(
          status_code=status.HTTP_404_NOT_FOUND,
          detail='Image not found'
        )
      
      image.predictions = json.dumps(predictions)
      session.add(image)
      session.commit()