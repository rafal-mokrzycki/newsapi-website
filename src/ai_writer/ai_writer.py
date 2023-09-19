import random
import re
from pathlib import Path

import repackage
from nltk import tokenize
from transformers import PegasusForConditionalGeneration, PegasusTokenizerFast, pipeline

repackage.up()
from config.config import load_config
from gcp_handler.gcp_handler import GCP_Handler
from utils.utils import CustomLogger

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
        # remove comma at the end of a headline
        if rewritten_headline.endswith("."):
            rewritten_headline = rewritten_headline[-1]
        self.rewritten_headline = rewritten_headline
        logger.info("Headline rewritten")
        return rewritten_headline

    def detect_topic(self) -> None:
        """Detects article topic and sets instance variable `topic`."""
        named_entities = self.get_named_entities()
        if named_entities is None:
            # If the article doesn't contain any named entity, \
            # detect general topic of the article
            logger.warning("Named entities not found in article")
            topic = self.classify_article_to_topic()
            self.topic = topic
            return topic
        per_named_entitites = self.get_named_entities_person(named_entities)
        if per_named_entitites is None:
            # If the article doesn't contain any PER (person) named entity, \
            # detect general topic of the article
            self.classify_article_to_topic()
        else:
            if self.mode == "no_gcp":
                # If the access to GCP is unabled assign PER named entity as a topic
                logger.info(
                    "Named entities not looked up in GCP due to \
                        mode='no_gcp'"
                )
                topic = random.choice(per_named_entitites)
                self.uri = "fake-uri"
                self.topic = topic
                return topic
            else:
                image_uri = GCP_Handler().get_random_image_of_person(
                    bucket_name="images", list_of_persons=per_named_entitites
                )
                if image_uri is None:
                    # If there is no image of a given person (PER named entity), \
                    # detect general topic of the article
                    logger.warning("Named entities not found in GCP")
                    topic = self.classify_article_to_topic()
                    self.topic = topic
                    return topic
                else:
                    # Otherwise, assing image URI found in GCP as self.uri
                    self.uri = image_uri
                    logger.info("Named entities found in GCP")

    # def detect_topic(self) -> None:
    #     """Detects article topic and sets instance variable `topic`."""
    #     named_entities = self.get_named_entities()
    #     # if there is a named entity PERSON in an article, return their name
    #     for ne in named_entities:
    #         if "PER" in ne.values():
    #             if self.mode == "no_gcp":
    #                 logger.info(
    #                     f"Named entity `{ne['word']}` not looked up in GCP due to \
    #                         mode='no_gcp'"
    #                 )
    #                 self.uri = "fake-uri"
    #                 self.topic = ne["word"]
    #                 return ne["word"]
    #             # if there is an image with this person in GCS return its URI
    #             # else continue
    #             else:
    #                 if GCP_Handler().is_person_in_gcs(
    #                     person=ne["word"], bucket_name="images"
    #                 ):
    #                     self.topic = ne["word"]
    #                     logger.info(f"Named entity `{ne['word']}` found in GCP")
    #                     return ne["word"]
    #                 else:
    #                     logger.warning(f"Named entity `{ne['word']}` not found in GCP")
    #                     continue
    #         else:
    #             continue
    #     # if no image of a person found or there is no person in named entities, \
    #     # detect a general topic of the article and return an image corrensponding to that
    #     classifier = pipeline(task="zero-shot-classification", model=CLASSIFICATION_MODEL)
    #     result = classifier(
    #         self.article,
    #         candidate_labels=CLASSES,
    #     )
    #     # return label where score is max
    #     scores_list = result["scores"]
    #     n_max = scores_list.index(max(scores_list))
    #     topic = result["labels"][n_max]
    #     self.topic = topic
    #     logger.info(f"`topic` set to {topic}")
    #     return topic

    def get_named_entities(self) -> list[dict]:
        """Returns named entities in an article"""
        token_classifier = pipeline(model=NER_MODEL, aggregation_strategy="simple")
        tokens = token_classifier(self.article)
        return tokens

    def get_named_entities_person(
        self, list_of_named_entities: list[dict]
    ) -> list[str] | None:
        """
        Returns named entities of type 'PER' (person) in a list of all named entities
        """
        list_of_per_named_entities = []
        for ne in list_of_named_entities:
            if "PER" in ne.values():
                list_of_per_named_entities.append(ne["word"])
            else:
                continue
        return list_of_per_named_entities if list_of_per_named_entities else None

    def classify_article_to_topic(
        self, article: str | None = None, candidate_labels: list[str] | None = None
    ) -> str:
        if article is None:
            article = self.article
        if candidate_labels is None:
            candidate_labels = CLASSES
        classifier = pipeline(task="zero-shot-classification", model=CLASSIFICATION_MODEL)
        result = classifier(
            article,
            candidate_labels,
        )
        # return label where score is max
        scores_list = result["scores"]
        n_max = scores_list.index(max(scores_list))
        topic = result["labels"][n_max]
        self.topic = topic
        logger.info(f"`topic` set to {topic}")
        return topic

    @staticmethod
    def add_html_advertisment(
        filtered_rewritten_sentences: list[str] | None = None,
    ) -> list[str]:
        html_code = """
<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-5880797269971404"
     crossorigin="anonymous"></script>
     """
        if filtered_rewritten_sentences is None:
            raise ValueError("filtered_rewritten_sentences cannot be None")
        filtered_rewritten_sentences_length = len(filtered_rewritten_sentences)
        if filtered_rewritten_sentences_length < 3:
            # If it's headline or an article is really short, don't add html_code
            return filtered_rewritten_sentences
        elif filtered_rewritten_sentences_length < 5:
            filtered_rewritten_sentences.append(html_code)
        elif filtered_rewritten_sentences_length < 8:
            index = filtered_rewritten_sentences_length // 2
            filtered_rewritten_sentences.insert(index, html_code)
        else:
            index_1 = filtered_rewritten_sentences_length // 3
            index_2 = index_1 * 2
            filtered_rewritten_sentences.insert(index_1, html_code)
            filtered_rewritten_sentences.insert(index_2, html_code)
        return filtered_rewritten_sentences

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
        # filter to replace 'CNN' with 'media'
        filtered_rewritten_sentences = [
            Filter.replace_unwanted_keywords(r_sentence).capitalize()
            for r_sentence in rewritten_sentences
        ]
        filtered_rewritten_sentences_with_advertisement = AI_Writer.add_html_advertisment(
            filtered_rewritten_sentences
        )
        return " ".join(filtered_rewritten_sentences_with_advertisement)


class Filter:
    def contains_pattern(pattern: str, string: str, flags: str | None = None) -> bool:
        if flags is None:
            flags = re.IGNORECASE
        if re.search(pattern, string, flags):
            return True
        return False

    def contains_video(string: str) -> bool:
        if re.search(r"video", string, re.IGNORECASE):
            return True
        return False

    def is_too_short_text(string: str) -> bool:
        sentences = tokenize.sent_tokenize(string)
        if len(sentences) < 3:
            return True
        return False

    def replace_unwanted_keywords(
        string: str, keywords: dict = {"CNN": "media"}
    ) -> list | None:
        for key, value in keywords.items():
            if re.search(key, string, re.IGNORECASE):
                string.replace(key, value)
        return string
