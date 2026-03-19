import os
import io
import vertexai
from vertexai.preview.vision_models import ImageGenerationModel
from dotenv import load_dotenv
import uuid
from typing import Union
from datetime import datetime
from google import genai
from google.genai import types
from google.adk.tools import ToolContext
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def create_image(prompt: str,tool_context: ToolContext) -> Union[bytes, str]:
  """
  Generates an image based on a text prompt using a Vertex AI Imagen model.
  Args:
      prompt: The text prompt to generate the image from.

  Returns:
      The binary image data (PNG format) on success, or an error message string on failure.
  """
  print(f"Attempting to generate image for prompt: '{prompt}'")

  try:
      # Load environment variables from .env file two levels up
      dotenv_path = os.path.join(os.path.dirname(__file__), '..', '..', '.env')
      load_dotenv(dotenv_path=dotenv_path)
      project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
      location = os.getenv("GOOGLE_CLOUD_LOCATION")
      model_name = os.getenv("IMAGEN_MODEL")
      client = genai.Client(
          vertexai=True,
          project=project_id,
          location=location,
      )
      response = client.models.generate_images(
          model="imagen-3.0-generate-002",
          prompt=prompt,
          config=types.GenerateImagesConfig(
              number_of_images=1,
              aspect_ratio="9:16",
              safety_filter_level="block_low_and_above",
              person_generation="allow_adult",
          ),
      )
      if not all([project_id, location, model_name]):
          return "Error: Missing GOOGLE_CLOUD_PROJECT, GOOGLE_CLOUD_LOCATION, or IMAGEN_MODEL in .env file."
      vertexai.init(project=project_id, location=location)
      model = ImageGenerationModel.from_pretrained(model_name)
      images = model.generate_images(
          prompt=prompt,
          number_of_images=1
      )
      if response.generated_images is  None:
          return "Error: No image was generated."
      for generated_image in response.generated_images:
          # Get the image bytes
          image_bytes = generated_image.image.image_bytes
          counter = str(tool_context.state.get("loop_iteration", 0))
          artifact_name = f"generated_image_" + counter + ".png"
          # Save as ADK artifact (optional, if still needed by other ADK components)
          report_artifact = types.Part.from_bytes(
              data=image_bytes, mime_type="image/png"
          )
          await tool_context.save_artifact(artifact_name, report_artifact)
          logger.info(f"Image also saved as ADK artifact: {artifact_name}")
          return {
              "status": "success",
              "message": f"Image generated .  ADK artifact: {artifact_name}.",
              "artifact_name": artifact_name,
          }
  except Exception as e:
      error_message = f"An error occurred during image generation: {e}"
      print(error_message)
      return error_message