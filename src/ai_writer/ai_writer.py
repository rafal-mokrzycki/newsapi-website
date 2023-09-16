import re
from pathlib import Path

import repackage
from transformers import pipeline

repackage.up()

from config.config import load_config
from gcp_handler.gcp_handler import GCP_Handler
from src.utils.utils import CustomLogger

NER_MODEL = "Jean-Baptiste/camembert-ner"
CLASSIFICATION_MODEL = "facebook/bart-large-mnli"
TEXT_GENERATION_MODEL = "EleutherAI/gpt-neo-125M"
CLASSES = ["education", "politics", "business", "cryptocurrency"]

config = load_config()
logger = CustomLogger(Path(__file__).name)


class AI_Writer:
    def __init__(self, headline: str, article: str, mode: str = "no_gcp") -> None:
        self.headline = headline
        self.article = article
        self.rewritten_headline = None
        self.rewritten_article = None
        self.topic = None
        self.uri = None
        self.mode = mode

    def rewrite_article(self) -> str:
        """Rewrites an article and sets instance variable `rewritten_article`"""
        rewritten_article = self.rewrite_text(
            input=self.article, max_length=None, n_sentences=25
        )
        self.rewritten_article = rewritten_article
        logger.info("Article rewritten")
        return rewritten_article

    def rewrite_headline(self) -> str:
        """Rewrites a headline and sets instance variable `rewritten_headline`"""
        rewritten_headline = self.rewrite_text(
            input=self.headline, max_length=None, n_sentences=1
        )
        self.rewritten_headline = rewritten_headline
        logger.info("Headline rewritten")
        return rewritten_headline

    def detect_topic(self) -> None:
        """Detects article topic and sets instance variable `topic`."""
        named_entities = self.get_named_entities()
        # if there is a named entity PERSON in an article, return their name
        for ne in named_entities:
            if "PER" in ne.values():
                if self.mode == "no_gcp":
                    logger.info(
                        f"Named entity `{ne['word']}` not looked up in GCP due to \
                            mode='no_gcp'"
                    )
                    self.uri = "fake-uri"
                    return ne["word"]
                # if there is an image with this person in GCS return its URI
                # else continue
                else:
                    if GCP_Handler().is_person_in_gcs(
                        person=ne["word"], bucket_name="images"
                    ):
                        self.topic = ne["word"]
                        logger.info(f"Named entity `{ne['word']}` found in GCP")
                        # TODO: set URI to self.uri
                        return ne["word"]
                    else:
                        logger.warning(f"Named entity `{ne['word']}` not found in GCP")
                        continue
        # if no image of a person found or there is no person in named entities, \
        # detect a general topic of the article and return an image corrensponding to that
        classifier = pipeline(task="zero-shot-classification", model=CLASSIFICATION_MODEL)
        result = classifier(
            self.article,
            candidate_labels=CLASSES,
        )
        # return label where score is max
        scores_list = result["scores"]
        n_max = scores_list.index(max(scores_list))
        topic = result["labels"][n_max]
        self.topic = topic
        logger.info(f"`topic` set to {topic}")
        return topic

    def get_named_entities(self) -> list[dict]:
        """Returns named entities in an article"""
        token_classifier = pipeline(model=NER_MODEL, aggregation_strategy="simple")
        tokens = token_classifier(self.article)
        return tokens

    @staticmethod
    def rewrite_text(
        input: str,
        temperature=0.6,
        max_length: int = None,
        n_sentences: int = None,
        task: str | None = None,
        model: str | None = None,
    ) -> str:
        """
        Rewrites text.

        Args:
            input (str): Text to rewrite.
            temperature (float):
            max_length (int, optional): Maximal length of the generated
            text. Defaults to 256.
            n_sentences (int, optional): Number of sentences to
            generate. Defaults to 1.

        Returns:
            str: Rewritten text.
        """
        # TODO: check another library
        # TODO: check another model
        number_of_tokens = len(re.findall(r"\b", input)) // 2
        max_length = number_of_tokens * 1.5 if max_length is None else max_length
        task = "text-generation" if task is None else task
        model = TEXT_GENERATION_MODEL if model is None else model
        generator = pipeline(task, model=model)
        generated_text = generator(
            input,
            do_sample=True,
            top_k=50,
            temperature=temperature,
            max_length=max_length,
            num_return_sequences=n_sentences,
            pad_token_id=generator.tokenizer.eos_token_id,
        )[0]["generated_text"]
        logger.info("Text generated")
        return generated_text
