"""Exercise the installed SDK's real serializer over an in-memory HTTP transport."""
import json
import httpx2
from openai import OpenAI

def test_responses_sdk_serialization_without_network():
    received = []
    payload = {
        "target_register": "academic",
        "overall_assessment": "Sem alterações.",
        "annotations": [],
        "transfer_pattern_summary": "Nenhum padrão.",
    }
    def respond(request):
        received.append(json.loads(request.content))
        assert request.url.path == "/v1/responses"
        return httpx2.Response(200, json={
            "id": "resp_offline", "object": "response", "created_at": 0,
            "status": "completed", "model": "gpt-5.6",
            "output": [{"id": "msg_offline", "type": "message", "role": "assistant",
                        "status": "completed", "content": [
                            {"type": "output_text", "text": json.dumps(payload), "annotations": []}
                        ]}],
        })
    with OpenAI(api_key="offline-placeholder-not-a-credential",
                base_url="https://offline.invalid/v1", max_retries=0,
                http_client=httpx2.Client(transport=httpx2.MockTransport(respond))) as client:
        result = client.responses.create(model="gpt-5.6", instructions="Offline fixture",
                                         input="Synthetic example",
                                         text={"format": {"type": "json_object"}})
    assert json.loads(result.output_text) == payload
    assert received[0]["text"] == {"format": {"type": "json_object"}}
    assert len(received) == 1
