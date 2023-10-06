import os
import random
import re
from pathlib import Path

import repackage
from nltk import tokenize
from tqdm.auto import tqdm
from transformers import PegasusForConditionalGeneration, PegasusTokenizerFast, pipeline

repackage.up()
from config.config import load_config
from gcp.gcs_handler import GCS_Handler
from news.news_handler import NewsHandler
from parsers.article_parser import get_original_article_text
from utilities.utils import CustomLogger, wait_for_web_scraping

config = load_config()

NER_MODEL = "Jean-Baptiste/camembert-ner"
CLASSIFICATION_MODEL = "facebook/bart-large-mnli"
TEXT_GENERATION_MODEL = "EleutherAI/gpt-neo-125M"
CLASSES = config["django"]["topics"]

logger = CustomLogger(Path(__file__).name)
# TODO: sth wrong with image assignement
# TODO: test and compare original text and rewritter article
# TODO: add filter for removing articles with less than 8 (5?) sentences


class AI_Writer:
    def __init__(self, headline: str, article: str, mode: str = "local") -> None:
        if mode.lower() not in config["django"]["modes"]:
            raise ValueError(f'mode must be one of {config["django"]["modes"]}')
        self.headline = headline
        self.article = article
        self.rewritten_headline = None
        self.rewritten_article = None
        self.topic = None
        self.uri = None
        self.author = random.choice(config["django"]["authors"])
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
            rewritten_headline = rewritten_headline[:-1]
        self.rewritten_headline = rewritten_headline
        logger.info("Headline rewritten")
        return rewritten_headline

    def detect_topic(self, **kwargs) -> None:
        """Detects article topic and sets instance variable `topic`."""
        named_entities = self.get_named_entities()
        if named_entities is None:
            # If the article doesn't contain any named entity, \
            # detect general topic of the article
            logger.warning("Named entities not found in article")
            topic = self.classify_article_to_topic(**kwargs)
            self.topic = topic
            return topic
        per_named_entitites = self.get_named_entities_person(named_entities)
        if per_named_entitites is None:
            # If the article doesn't contain any PER (person) named entity, \
            # detect general topic of the article
            topic = self.classify_article_to_topic(**kwargs)
            self.topic = topic
            return topic
        else:
            if self.mode == "local":
                # If the access to GCP is unabled assign PER named entity as a topic
                topic = self.classify_article_to_topic(**kwargs)
                image_path = self.get_random_image_of_person(
                    list_of_persons=per_named_entitites
                )
                logger.info(
                    "Named entities looked up locally due to \
                        mode='local'"
                )
                if image_path is not None:
                    self.uri = f"images/{image_path}"
                    return topic
                else:
                    # if image for any person not found, get image for a topic
                    for per in per_named_entitites:
                        logger.error(f"Image(s) of {per} not found")
                    image_path = self.get_random_image_of_person(
                        list_of_persons=[self.topic]
                    )
                    self.uri = f"images/{image_path}"
                    return topic
            else:
                image_uri = GCS_Handler().get_random_image_of_person(
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

    def get_random_image_of_person(self, list_of_persons: list[str]) -> str | None:
        """Returns a random image of a person"""
        list_of_persons_images = []
        for person in list_of_persons:
            person_snake_case = person.lower().replace(
                " ", "_"
            )  # Donald Trump -> donald_trump
            for file in os.listdir("images"):
                # match only regular images, not cropped ones
                if person_snake_case in file and re.match(r".*_\d+.jpg", file):
                    list_of_persons_images.append(file)
        if list_of_persons_images:
            return random.choice(list_of_persons_images)
        return

    def classify_article_to_topic(
        self, article: str | None = None, candidate_labels: list[str] | None = None
    ) -> str:
        """
        Classifies an article to a topic based on the content.

        Args:
            article (str | None, optional): Article content. If None taken from class
            variable `article`. Defaults to None.
            candidate_labels (list[str] | None, optional): Classes to pick from. If None
            taken from script variable `CLASSES`. Defaults to None.

        Returns:
            str: Article topic.
        """
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
    def get_actual_named_entities():
        """
        Helper function to get all named entities in first 15 articles from NewsHandler.
        """
        news_handler = NewsHandler()
        news = news_handler.get_top_headlines(page=1, page_size=15)
        list_of_actual_named_entities = []
        for new in tqdm(news):
            headline, article = get_original_article_text(new[0], new[1])
            ai_writer = AI_Writer(headline, article)
            ne_list = ai_writer.get_named_entities()
            ne_person_list = ai_writer.get_named_entities_person(ne_list)
            for person in tqdm(ne_person_list):
                list_of_actual_named_entities.append(person)
            wait_for_web_scraping()
        with open("list_of_actual_named_entities.txt", "a+") as file:
            for ne in set(list_of_actual_named_entities):
                file.write(f"{ne}\n")

    @staticmethod
    def add_html_advertisment(
        filtered_rewritten_sentences: list[str] | None = None,
    ) -> list[str]:
        html_code = """"""
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
        filtered_rewritten_sentences = []
        for r_sentence in rewritten_sentences:
            filtered_r_sentence = Filter.replace_unwanted_keywords(r_sentence)
            filtered_rewritten_sentences.append(
                f"{filtered_r_sentence[0].upper()}{filtered_r_sentence[1:]}"
            )
        filtered_rewritten_sentences_with_advertisement = AI_Writer.add_html_advertisment(
            filtered_rewritten_sentences
        )
        return " ".join(filtered_rewritten_sentences_with_advertisement)


class Filter:
    def contains_pattern(pattern: str, string: str, flags: str | None = None) -> bool:
        """
        Checks if a given string contains a substring matching (re.)pattern.

        Args:
            pattern (str): Pattern to check string against.
            string (str): String to check.
            flags (str | None, optional): Flags to add to `re.search` function. If None
            equal to re.IGNORECASE. Defaults to None.

        Returns:
            bool: True if string contains a substring, False otherwise.
        """
        if flags is None:
            flags = re.IGNORECASE
        if re.search(pattern, string, flags):
            return True
        return False

    def contains_video(string: str) -> bool:
        """
        Returns True if `string` contains `video` substring (case insensitive),
        False otherwise.
        """
        if re.search(r"video", string, re.IGNORECASE):
            return True
        return False

    def is_too_short_text(string: str) -> bool:
        """
        Returns True if `string` is shorter than 3 sentences, False otherwise.
        """
        sentences = tokenize.sent_tokenize(string)
        if len(sentences) < 3:
            return True
        return False

    def replace_unwanted_keywords(string: str, keywords: dict | None = None) -> str:
        """
        Replaces substrings (keys from `keywords`) with values from `keywords`
        in a string.

        Args:
            string (str): String to change.
            keywords (dict | None, optional): Dictionary to take substrings to swap from.
            If None equals to {"CNN": "media"}. Defaults to None.

        Returns:
            str: String with replacements.
        """
        if keywords is None:
            keywords = {"CNN": "media"}
        for key, value in keywords.items():
            if re.search(key, string, re.IGNORECASE) is not None:
                string = string.replace(key, value)
        return string


if __name__ == "__main__":
    AI_Writer.get_actual_named_entities()
