from pathlib import Path

import repackage
from nltk import tokenize
from transformers import PegasusForConditionalGeneration, PegasusTokenizerFast, pipeline

repackage.up()

from config.config import load_config
from gcp_handler.gcp_handler import GCP_Handler
from src.utils.utils import CustomLogger

NER_MODEL = "Jean-Baptiste/camembert-ner"
CLASSIFICATION_MODEL = "facebook/bart-large-mnli"
TEXT_GENERATION_MODEL = "EleutherAI/gpt-neo-125M"
CLASSES = ["education", "politics", "business", "cryptocurrency", "economy", "war"]

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
        rewritten_article = self.rewrite_text(input_=self.article)
        self.rewritten_article = rewritten_article
        logger.info("Article rewritten")
        return rewritten_article

    def rewrite_headline(self) -> str:
        """Rewrites a headline and sets instance variable `rewritten_headline`"""
        rewritten_headline = self.rewrite_text(input_=self.headline)
        self.rewritten_headline = rewritten_headline
        logger.info("Headline rewritten")
        return rewritten_headline

    def detect_topic(self) -> None:
        """Detects article topic and sets instance variable `topic`."""
        named_entities = self.get_named_entities()
        # if there is a named entity PERSON in an article, return their name
        # TODO: change for gathering all NEs PERSON, compare any of them againt \
        # Google Storage and only if none is found, try to find a general topic
        # TODO: add filter Videos (if video found, omit)
        # TODO: add filter for too short articles
        for ne in named_entities:
            if "PER" in ne.values():
                if self.mode == "no_gcp":
                    logger.info(
                        f"Named entity `{ne['word']}` not looked up in GCP due to \
                            mode='no_gcp'"
                    )
                    self.uri = "fake-uri"
                    self.topic = ne["word"]
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
            else:
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
        input_: str, num_beams: int = 10, num_return_sequences: int = 10
    ) -> str:
        """
        Rewrites text.

        Args:
            input_ (str): Text to rewrite.

        Returns:
            str: Rewritten text.
        """
        # TODO: better model?
        # TODO: add filter to remove sentences, where CNN appears
        model = PegasusForConditionalGeneration.from_pretrained(
            "tuner007/pegasus_paraphrase"
        )
        tokenizer = PegasusTokenizerFast.from_pretrained("tuner007/pegasus_paraphrase")
        sentences = tokenize.sent_tokenize(input_)
        rewritten_sentences = []
        for sentence in sentences:
            # tokenize the text to be form of a list of token IDs
            inputs = tokenizer(
                [sentence], truncation=True, padding="longest", return_tensors="pt"
            )
            # generate the paraphrased sentences
            outputs = model.generate(
                **inputs,
                num_beams=num_beams,
                num_return_sequences=num_return_sequences,
            )
            # decode the generated sentences using the tokenizer to get them back to text
            rewritten_sentences.append(
                tokenizer.batch_decode(outputs, skip_special_tokens=True)[0]
            )
        return " ".join([r_sentence for r_sentence in rewritten_sentences])
