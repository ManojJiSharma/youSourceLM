from pymupdf import pymupdf
import fitz
import os
from langchain_core.documents import Document

output_path = 'output/'


def extract_text(file_path) -> str:
    text = []
    content = fitz.open(file_path)

    for page_number, page in enumerate(content):
        page_text = page.get_text("text")

        if page_text.strip():
            text.append(Document(
                page_content=page_text,
                metadata={
                    "page": page_number+1,
                    "text": page_text
                }))
    return text


def extract_images(file_path, output_path):
    os.makedirs(output_path, exist_ok=True)

    image_paths = []
    seen_xrefs = set()

    content = fitz.open(file_path)
    for page_number, page in enumerate(content):
        image_list = page.get_images(full=True)

        for image_index, img in enumerate(image_list):
            xref = img[0]

            if xref in seen_xrefs:
                continue

            seen_xrefs.add(xref)

            base_image = content.extract_image(xref)

            image_bytes = base_image["image"]
            image_ext = base_image["ext"]

            image_filename = f"page{page_number+1+len(content)}_img{image_index+1}.{image_ext}"
            image_path = os.path.join(output_path, image_filename)

            with open(image_path, "wb") as img_file:
                img_file.write(image_bytes)

            image_paths.append(image_path)

    return image_paths

