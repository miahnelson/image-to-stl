import os
import cv2
import numpy as np
from stl import mesh
import pymeshfix

class LithophaneCreator:
    """
    Class for creating a lithophane from an image.

    Attributes:
        max_depth (int): Maximum depth for the lithophane.
        base_thickness (int): Base thickness for the lithophane.
        output_width (int): Output width of the lithophane in pixels.
        invert (bool): Flag to invert the depth of the lithophane.
        resolution (float): Resolution factor for resizing the image.
        smoothness (int): Smoothness factor for Gaussian blur.
        grayscale (bool): Flag to convert the image to grayscale.
        top_surface_smoothness (int): Smoothness factor for the top surface.
        repair_mesh (bool): Flag to perform mesh repair using PyMeshFix.
    """
    def __init__(self, max_depth, base_thickness, output_width, invert, resolution, smoothness, grayscale, top_surface_smoothness, repair_mesh=True):
        self.max_depth = max_depth
        self.base_thickness = base_thickness
        self.output_width = output_width
        self.invert = invert
        self.resolution = resolution
        self.smoothness = smoothness
        self.grayscale = grayscale
        self.top_surface_smoothness = top_surface_smoothness
        self.repair_mesh = repair_mesh

    def create_lithophane(self, image_path, output_path):
        """
        Create a lithophane from the provided image and save it as an STL file.

        Args:
            image_path (str): Path to the input image file.
            output_path (str): Path to the output STL file.

        Returns:
            str: Path to the fixed STL file, or original STL file if repair is not performed.
        """
        # Load the image
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError("Image not found or unable to load")

        # Optionally convert to grayscale
        if self.grayscale:
            image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # Adjust resolution
        if self.resolution != 1.0:
            image = cv2.resize(image, (0, 0), fx=self.resolution, fy=self.resolution, interpolation=cv2.INTER_AREA)

        # If the image is not already grayscale, convert it
        if len(image.shape) == 3:
            image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # Normalize the image to the range [0, 1]
        normalized_image = image / 255.0

        # Optionally invert the image so that light areas are raised
        if self.invert:
            depth_image = normalized_image * self.max_depth
        else:
            # Invert the image so that dark areas are raised
            inverted_image = 1.0 - normalized_image
            depth_image = inverted_image * self.max_depth

        # Apply smoothness (Gaussian blur) to the depth image
        if self.smoothness > 0:
            depth_image = cv2.GaussianBlur(depth_image, (self.smoothness, self.smoothness), 0)

        # Check the shape of the depth_image to ensure it's 2D
        if len(depth_image.shape) != 2:
            raise ValueError(f"depth_image has an unexpected shape: {depth_image.shape}")

        # Get the dimensions of the input image
        height, width = depth_image.shape

        # Calculate the scaling factor for the width
        x_scale = self.output_width / width
        # Calculate the new height based on the aspect ratio
        output_height = height * x_scale

        # Apply top surface smoothing using Gaussian blur
        if self.top_surface_smoothness > 0:
            depth_image = cv2.GaussianBlur(depth_image, (self.top_surface_smoothness, self.top_surface_smoothness), 0)

        # Create a 3D model from the depth image
        vertices = []
        faces = []

        # Generate top vertices
        for y in range(height):
            for x in range(width):
                z = depth_image[y, x] + self.base_thickness
                vertices.append([x * x_scale, y * x_scale, z])

        # Generate bottom vertices
        for y in range(height):
            for x in range(width):
                vertices.append([x * x_scale, y * x_scale, 0])

        # Generate faces for the top surface
        for y in range(height - 1):
            for x in range(width - 1):
                v1 = y * width + x
                v2 = v1 + 1
                v3 = v1 + width
                v4 = v3 + 1
                faces.append([v1, v2, v3])
                faces.append([v2, v4, v3])

        # Generate faces for the bottom surface
        offset = height * width
        for y in range(height - 1):
            for x in range(width - 1):
                v1 = y * width + x + offset
                v2 = v1 + 1
                v3 = v1 + width
                v4 = v3 + 1
                faces.append([v1, v3, v2])
                faces.append([v2, v3, v4])

        # Generate faces for the sides
        for y in range(height - 1):
            for x in range(width - 1):
                v1_top = y * width + x
                v2_top = v1_top + 1
                v1_bottom = v1_top + offset
                v2_bottom = v1_bottom + 1
                faces.append([v1_top, v2_top, v1_bottom])
                faces.append([v2_top, v2_bottom, v1_bottom])

                v3_top = v1_top + width
                v4_top = v3_top + 1
                v3_bottom = v3_top + offset
                v4_bottom = v3_bottom + 1
                faces.append([v3_top, v4_top, v3_bottom])
                faces.append([v4_top, v4_bottom, v3_bottom])

        vertices = np.array(vertices)
        faces = np.array(faces)

        # Create the mesh
        lithophane_mesh = mesh.Mesh(np.zeros(faces.shape[0], dtype=mesh.Mesh.dtype))
        for i, face in enumerate(faces):
            for j in range(3):
                lithophane_mesh.vectors[i][j] = vertices[face[j], :]

        # Save the mesh to an STL file
        lithophane_mesh.save(output_path)

        if self.repair_mesh:
            # Post-process the STL file using PyMeshFix
            meshfix = pymeshfix.MeshFix(vertices, faces)
            meshfix.repair()
            vertices_fixed, faces_fixed = meshfix.return_arrays()

            # Create a fixed mesh
            fixed_mesh = mesh.Mesh(np.zeros(faces_fixed.shape[0], dtype=mesh.Mesh.dtype))
            for i, face in enumerate(faces_fixed):
                for j in range(3):
                    fixed_mesh.vectors[i][j] = vertices_fixed[face[j], :]

            # Save the fixed mesh to an STL file
            fixed_output_path = output_path.replace(".stl", "_fixed.stl")
            fixed_mesh.save(fixed_output_path)
            return fixed_output_path
        else:
            return output_path

if __name__ == "__main__":
    processor = LithophaneCreator(
        max_depth=10,
        base_thickness=4,
        output_width=200,
        invert=True,
        resolution=0.5,
        smoothness=1,
        grayscale=True,
        top_surface_smoothness=9,
        repair_mesh=True
    )

    input_image_path = "./uploads/test.jpg"  # Provide a valid test image path
    output_stl_path = "./outputs/test_output.stl"

    if os.path.exists(input_image_path):
        fixed_output_path = processor.create_lithophane(input_image_path, output_stl_path)
        print(f"Lithophane created successfully: {fixed_output_path}")
    else:
        print(f"Input image path does not exist: {input_image_path}")
