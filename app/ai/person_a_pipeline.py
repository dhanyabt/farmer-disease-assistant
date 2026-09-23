from pathlib import Path

from quality_gate import check_image_quality
from classifier import load_model, predict_image


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

    # Step 2: Load trained disease model
    model = load_model()

    # Step 3: Predict disease
    prediction = predict_image(
        image_path,
        model
    )

    # Step 4: Return clean output
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