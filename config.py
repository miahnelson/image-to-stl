from dotenv import load_dotenv
import os

load_dotenv()

class Config:
    """
    Configuration class to load environment variables from a .env file.

    Attributes:
        MAX_DEPTH (int): Maximum depth for the lithophane.
        BASE_THICKNESS (int): Base thickness for the lithophane.
        OUTPUT_WIDTH (int): Output width of the lithophane in pixels.
        RESOLUTION (float): Resolution factor for resizing the image.
        SMOOTHNESS (int): Smoothness factor for Gaussian blur.
        GRAY_SCALE (bool): Flag to convert the image to grayscale.
        TOP_SURFACE_SMOOTHNESS (int): Smoothness factor for the top surface.
        INVERT (bool): Flag to invert the depth of the lithophane.
    """
    MAX_DEPTH = int(os.getenv('MAX_DEPTH', 10))
    BASE_THICKNESS = int(os.getenv('BASE_THICKNESS', 4))
    OUTPUT_WIDTH = int(os.getenv('OUTPUT_WIDTH', 200))
    RESOLUTION = float(os.getenv('RESOLUTION', 0.5))
    SMOOTHNESS = int(os.getenv('SMOOTHNESS', 1))
    GRAY_SCALE = os.getenv('GRAY_SCALE', 'True').lower() == 'true'
    TOP_SURFACE_SMOOTHNESS = int(os.getenv('TOP_SURFACE_SMOOTHNESS', 9))
    INVERT = os.getenv('INVERT', 'False').lower() == 'true'
