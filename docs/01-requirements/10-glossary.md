| Term   | Definition                                                                         |
| ------ | ---------------------------------------------------------------------------------- |
| AI Evaluation Engine | A modular system that processes answer scripts through a pipeline (OCR, preprocessing, segmentation, rubric matching, LLM analysis) to generate scoring suggestions. |
| Answer Segmentation | The process of identifying and isolating the text of a specific answer within a larger body of text. |
| Confidence Validation | The process of calculating a confidence score for an AI-generated evaluation to indicate its reliability. |
| OCR    | Optical Character Recognition                                                      |
| AI     | Artificial Intelligence                                                            |
| LLM Provider | An abstraction layer that interfaces with various Large Language Model APIs (e.g., Gemini, OpenAI), allowing the system to be model-agnostic. |
| Prompt Builder | A component that constructs a detailed, structured prompt for an LLM, combining the answer text, rubric criteria, and formatting instructions. |
| Question Detection | The process of automatically identifying question numbers or markers within the extracted text of an answer script. |
| Rubric | Question evaluation criteria                                                       |
| Rubric Engine | A component that programmatically matches a student's answer to the relevant grading rubric before evaluation. |
| Score Normalization | The process of converting scores from various LLM outputs into a consistent, predefined scale used by the system. |
| Structured JSON Response | A machine-readable format for LLM output, ensuring that scoring, explanations, and feedback are delivered consistently and can be parsed by the system. |
| ETA    | Estimated Time of Arrival *(Not applicable here—don't include unrelated terms.)* |
| RBAC   | Role-Based Access Control                                                          |
