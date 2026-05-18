from usecases.grade_submission import grade_submission


image_path = "answers/sample_0.jpg"

result = grade_submission(image_path)

print("===== TEST ID =====")
print(result["test_id"])

print("===== RESULT =====")
print(result["result"])

print("===== LINE Message =====")
print(result["message"])