from langchain_ollama import OllamaLLM
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
import logging

logger = logging.getLogger(__name__)

class StoryGeneratorService:
    def __init__(self):
        # You can also use other free options like HuggingFace transformers
        try:
            self.llm = OllamaLLM(model="gemma:2b")
        except Exception as e:
            logger.error(f"Failed to initialize Ollama: {e}")
            # Fallback to a simple mock generator for demonstration
            self.llm = None
    
    def generate_story(self, prompt, length='medium', genre='fantasy'):
        """Generate a short story based on the given prompt"""
        
        length_instructions = {
            'short': 'Write a short story of about 50-100 words.',
            'medium': 'Write a medium-length story of about 100-200 words.',
            'long': 'Write a longer story of about 200-250 words.'
        }
        
        story_template = PromptTemplate(
            input_variables=["prompt", "genre", "length_instruction"],
            template="""
            {length_instruction}
            
            Genre: {genre}
            
            Based on this prompt: {prompt}
            
            Create an engaging story with:
            - A compelling protagonist
            - Clear beginning, middle, and end
            - Vivid descriptions
            - Dialogue where appropriate
            - A satisfying conclusion
            
            Story:
            """
        )
        
        if self.llm is None:
            # Fallback mock story for demonstration
            return self._generate_mock_story(prompt, genre)
        
        try:
            chain = story_template | self.llm | StrOutputParser()
            
            story = chain.invoke({
                "prompt": prompt,
                "genre": genre,
                "length_instruction": length_instructions[length]
            })
            
            return story.strip()
            
        except Exception as e:
            logger.error(f"Error generating story: {e}")
            return self._generate_mock_story(prompt, genre)
    
    def generate_character_description(self, story):
        """Extract and describe the main character from the story"""
        
        character_template = PromptTemplate(
            input_variables=["story"],
            template="""
            Based on this story: {story}
            
            Provide a brief character description of the main protagonist including:
            - Physical appearance
            - Personality traits
            - Key motivations   
            
            Character Description:
            """
        )
        
        if self.llm is None:
            return "A brave and curious protagonist who faces challenges with determination and grows throughout their journey."
        
        try:
            chain = character_template | self.llm | StrOutputParser()
            description = chain.invoke({"story": story})
            return description.strip()
            
        except Exception as e:
            logger.error(f"Error generating character description: {e}")
            return "A brave and curious protagonist who faces challenges with determination and grows throughout their journey."
    
    def generate_background_description(self, story):
        """Extract and describe the main character from the story"""
        
        character_template = PromptTemplate(
            input_variables=["story"],
            template="""
            Based on this story: {story}
            
            Provide a brief background description of the setting in the story.
            
            Background Description:
            """
        )
        
        if self.llm is None:
            return "A bright and happening city where everyone is continuously busy."
        
        try:
            chain = character_template | self.llm | StrOutputParser()
            description = chain.invoke({"story": story})
            return description.strip()
            
        except Exception as e:
            logger.error(f"Error generating character description: {e}")
            return "A brave and curious protagonist who faces challenges with determination and grows throughout their journey."
    

    def _generate_mock_story(self, prompt, genre):
        """Fallback mock story generator"""
        return f"""
        In the realm of {genre}, where {prompt.lower()}, our story begins.

        Sarah had always been drawn to the mysterious. As she approached the ancient oak tree that had appeared overnight in her backyard, she felt a familiar tingle of excitement mixed with apprehension. The tree seemed to shimmer with an otherworldly energy, its bark etched with symbols she couldn't understand.

        "This can't be real," she whispered to herself, reaching out to touch the rough bark. The moment her fingers made contact, the world around her shifted.

        Suddenly, she found herself in a vast library filled with floating books and glowing orbs of light. The air hummed with magic, and she could hear whispers from the books as they drifted past. An elderly woman with silver hair appeared from behind a towering bookshelf.

        "Welcome, Sarah," the woman said with a knowing smile. "We've been waiting for you."

        "Waiting for me? But I don't understand—"

        "You have the gift," the woman interrupted gently. "The ability to step between worlds, to read the stories that exist between the lines of reality. This library contains every story that has ever been imagined, and every story yet to be told."

        Sarah's heart raced as she looked around at the impossible sight. Books of every size and color floated gracefully through the air, some open, their pages turning on their own, others closed and glowing with inner light.

        "What am I supposed to do?" Sarah asked.

        "Choose a story," the woman replied, gesturing to the floating books. "Any story. Step inside it, live it, and help it reach its proper ending. Some stories have gone astray, lost their way. They need a guide."

        With trembling hands, Sarah reached for a small, leather-bound book that glowed with soft golden light. As she opened it, the world dissolved around her once again, and she felt herself falling into a new adventure.

        When she finally returned home hours later, the oak tree was gone, but Sarah carried with her the knowledge that magic existed everywhere, waiting for those brave enough to seek it.
        """