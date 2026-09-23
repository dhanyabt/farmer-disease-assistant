from pathlib import Path

from app.ai.quality_gate import check_image_quality
from app.ai.classifier import CONFIDENCE_THRESHOLD, classify_image


def analyze_image(image_path: str) -> dict:
    """
    Complete Person A pipeline:
    1. Check image quality
    2. If accepted, run disease classifier
    3. Return result for the main HACKMINT system
    """

    # Step 1: Image Quality Gate
    quality = check_image_quality(image_path)

    if not quality["accepted"]:
        return {
            "status": "rejected",
            "reason": "image_quality",
            "image_quality": quality,
        }

    

    # Step 2: Predict disease
    prediction = classify_image(
        image_path,
        CONFIDENCE_THRESHOLD
    )

    # Step 3: Return clean output
    return {
        "status": "success",
        "image_quality": {
            "accepted": quality["accepted"],
            "blur_score": quality["blur_score"],
        },
        "prediction": {
            "crop": prediction["crop"],
            "disease": prediction["disease"],
            "confidence": prediction["confidence"],
        },
    }


if __name__ == "__main__":

    test_image = "test_images/tomato_leaf.png"

    result = analyze_image(test_image)

    print("\nHACKMINT PERSON A RESULT")
    print("========================")
    print(result)