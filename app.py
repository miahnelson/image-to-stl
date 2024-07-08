import os
import threading
import traceback
import uuid
from flask import Flask, request, render_template, jsonify, url_for, send_file
from werkzeug.utils import secure_filename
from image_processing import LithophaneCreator
from config import Config

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['OUTPUT_FOLDER'] = 'outputs'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg'}

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

if not os.path.exists(app.config['OUTPUT_FOLDER']):
    os.makedirs(app.config['OUTPUT_FOLDER'])

def allowed_file(filename):
    """
    Check if the uploaded file is allowed based on its extension.

    Args:
        filename (str): Name of the uploaded file.

    Returns:
        bool: True if the file is allowed, False otherwise.
    """
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def validate_int_input(value, min_value, max_value, default_value):
    """
    Validate integer input from the form.

    Args:
        value (str): The input value to validate.
        min_value (int): Minimum allowed value.
        max_value (int): Maximum allowed value.
        default_value (int): Default value to return if validation fails.

    Returns:
        int: The validated integer value.
    """
    try:
        value = int(value)
        if value < min_value or value > max_value:
            return default_value
        return value
    except:
        return default_value

def validate_float_input(value, min_value, max_value, default_value):
    """
    Validate float input from the form.

    Args:
        value (str): The input value to validate.
        min_value (float): Minimum allowed value.
        max_value (float): Maximum allowed value.
        default_value (float): Default value to return if validation fails.

    Returns:
        float: The validated float value.
    """
    try:
        value = float(value)
        if value < min_value or value > max_value:
            return default_value
        return value
    except:
        return default_value

def process_image(filepath, output_filepath, max_depth, base_thickness, output_width, invert, resolution, smoothness, grayscale, top_surface_smoothness, repair_mesh):
    """
    Process the image and create a lithophane STL file.

    Args:
        filepath (str): Path to the input image file.
        output_filepath (str): Path to the output STL file.
        max_depth (int): Maximum depth for the lithophane.
        base_thickness (int): Base thickness for the lithophane.
        output_width (int): Output width of the lithophane in pixels.
        invert (bool): Flag to invert the depth of the lithophane.
        resolution (float): Resolution factor for resizing the image.
        smoothness (int): Smoothness factor for Gaussian blur.
        grayscale (bool): Flag to convert the image to grayscale.
        top_surface_smoothness (int): Smoothness factor for the top surface.
        repair_mesh (bool): Flag to perform mesh repair using PyMeshFix.

    Returns:
        str: Path to the fixed STL file.
    """
    try:
        processor = LithophaneCreator(
            max_depth=max_depth,
            base_thickness=base_thickness,
            output_width=output_width,
            invert=invert,
            resolution=resolution,
            smoothness=smoothness,
            grayscale=grayscale,
            top_surface_smoothness=top_surface_smoothness,
            repair_mesh=repair_mesh
        )
        return processor.create_lithophane(filepath, output_filepath)
    except Exception as e:
        print(f"Error processing image: {str(e)}")
        traceback.print_exc()

@app.route('/', methods=['GET', 'POST'])
def index():
    """
    Handle the index page and form submissions for creating a lithophane.

    Returns:
        str: The rendered HTML template or a JSON response.
    """
    if request.method == 'POST':
        try:
            if 'file' not in request.files:
                return jsonify({"success": False, "error": "No file part"})
            file = request.files['file']
            if file.filename == '':
                return jsonify({"success": False, "error": "No selected file"})
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)

                # Get form data and validate
                max_depth = validate_int_input(request.form.get('max_depth'), 1, 10, Config.MAX_DEPTH)
                base_thickness = validate_int_input(request.form.get('base_thickness'), 1, 5, Config.BASE_THICKNESS)
                output_width = validate_int_input(request.form.get('output_width'), 100, 2000, Config.OUTPUT_WIDTH)
                resolution = validate_float_input(request.form.get('resolution'), 0.1, 10.0, Config.RESOLUTION)
                smoothness = validate_int_input(request.form.get('smoothness'), 1, 20, Config.SMOOTHNESS)
                top_surface_smoothness = validate_int_input(request.form.get('top_surface_smoothness'), 1, 20, Config.TOP_SURFACE_SMOOTHNESS)

                invert = request.form.get('invert', 'false').lower() == 'true'
                grayscale = request.form.get('grayscale', 'false').lower() == 'true'
                repair_mesh = request.form.get('repair_mesh', 'false').lower() == 'true'

                unique_filename = f"{uuid.uuid4().hex}.stl"
                output_filepath = os.path.join(app.config['OUTPUT_FOLDER'], unique_filename)

                thread = threading.Thread(
                    target=process_image, 
                    args=(filepath, output_filepath, max_depth, base_thickness, output_width, invert, resolution, smoothness, grayscale, top_surface_smoothness, repair_mesh)
                )
                thread.start()
                thread.join()

                fixed_output_filename = unique_filename.replace(".stl", "_fixed.stl") if repair_mesh else unique_filename
                return jsonify({"success": True, "stl_url": url_for('download_file', filename=fixed_output_filename)})
        except Exception as e:
            traceback.print_exc()
            return jsonify({"success": False, "error": str(e)})

    return render_template('index.html', config=Config)

@app.route('/logs')
def logs():
    """
    Handle the logs endpoint to return log messages.

    Returns:
        str: JSON response with log messages.
    """
    return jsonify({"logs": []})

@app.route('/download/<filename>')
def download_file(filename):
    """
    Handle file download requests.

    Args:
        filename (str): Name of the file to download.

    Returns:
        str: The file to download.
    """
    filepath = os.path.join(app.config['OUTPUT_FOLDER'], filename)
    return send_file(filepath, as_attachment=True)

@app.route('/viewer')
def viewer():
    """
    Handle the STL viewer page.

    Returns:
        str: The rendered HTML template for the STL viewer.
    """
    return render_template('viewer.html')

if __name__ == '__main__':
    app.run(debug=True)
