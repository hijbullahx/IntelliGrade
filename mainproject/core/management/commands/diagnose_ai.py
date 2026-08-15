from django.core.management.base import BaseCommand
from config.ai_config import get_ai_config, AIConfig
from config.evaluation_config import get_evaluation_config
from config import get_config_fingerprint

class Command(BaseCommand):
    help = 'Safely reports AI provider failover architecture, model configurations, evaluation thresholds, and API readiness.'

    def handle(self, *args, **options):
        self.stdout.write("=" * 65)
        self.stdout.write("            INTELLIGRADE GLOBAL AI ENGINE DIAGNOSTIC")
        self.stdout.write("=" * 65)

        fingerprints = get_config_fingerprint()
        ai_info = get_ai_config()
        eval_info = get_evaluation_config()

        self.stdout.write(f"\nPrompt Version    : {fingerprints['prompt_version']}")
        self.stdout.write(f"AI Config Version : {fingerprints['ai_config_version']}")
        self.stdout.write(f"Primary Provider  : {ai_info['default_provider']}")
        self.stdout.write(f"Failover Chain    : {' -> '.join(AIConfig.FAILOVER_SEQUENCE)}")

        self.stdout.write(f"\n[PROVIDER CONFIGURATIONS]")
        for p in ["GEMINI", "GROQ", "OPENAI", "OLLAMA", "MOCK"]:
            key = AIConfig.get_api_key(p)
            status = "CONFIGURED" if (key or p in ["OLLAMA", "MOCK"]) else "MISSING"
            models = AIConfig.get_provider_models(p)
            self.stdout.write(f"{p:<8} : Status={status:<12} | Active Models={models}")

        self.stdout.write(f"\n[EVALUATION HYPERPARAMETERS]")
        self.stdout.write(f"Temperature       : {eval_info['temperature']}")
        self.stdout.write(f"Max Tokens        : {eval_info['max_tokens']}")
        self.stdout.write(f"Request Timeout   : {eval_info['timeout_seconds']}s")
        self.stdout.write(f"Confidence Thresh : {eval_info['confidence_threshold']}")
        self.stdout.write(f"Manual Review Thr : {eval_info['manual_review_threshold']}")
        self.stdout.write(f"RAG Exemplars     : {'ENABLED' if eval_info['enable_rag_learning'] else 'DISABLED'}")

        self.stdout.write("\n" + "=" * 65)
        self.stdout.write(self.style.SUCCESS("AI DIAGNOSTIC COMPLETED PASSING"))
        self.stdout.write("=" * 65 + "\n")
