from langchain_ollama import OllamaLLM
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
import logging

logger = logging.getLogger(__name__)

class StoryGeneratorService:
    def __init__(self):
        try:
            self.llm = OllamaLLM(model="gemma:2b")
        except Exception as e:
            logger.error(f"Failed to initialize Ollama: {e}")
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
            
            Create an engaging story with a compelling protagonist, clear beginning/middle/end, 
            vivid descriptions, dialogue where appropriate, and a satisfying conclusion.
            
            Story:
            """
        )
        
        if not self.llm:
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
            
            Create a comprehensive character profile including:
            PHYSICAL APPEARANCE: Age, build, hair, eyes, clothing, distinctive features
            PERSONALITY: Core traits, strengths, flaws, quirks, social interactions
            BACKGROUND: Family, education, experiences, formative events
            MOTIVATIONS: Drives, desires, fears, goals
            SKILLS: Talents, abilities, interests, strengths/weaknesses
            
            Write as a detailed character analysis in 150-200 words.
            
            Character Description:
            """
        )
        
        if not self.llm:
            return self._generate_mock_character_description()
        
        try:
            chain = character_template | self.llm | StrOutputParser()
            return chain.invoke({"story": story}).strip()
        except Exception as e:
            logger.error(f"Error generating character description: {e}")
            return self._generate_mock_character_description()
    
    def generate_background_description(self, story, genre):
        """Generate detailed background/setting description from the story"""
        
        background_template = PromptTemplate(
            input_variables=["story", "genre"],
            template="""
            Based on this {genre} story: {story}
            
            Create a rich world description including:
            PHYSICAL ENVIRONMENT: Geography, climate, architecture, natural features
            TIME/HISTORY: When it occurs, historical context, technology/magic level
            SOCIETY/CULTURE: Social structure, traditions, languages, beliefs
            POLITICS/ECONOMICS: Government, laws, economy, military
            UNIQUE ELEMENTS: Special features, magical systems, mysteries, lore
            DAILY LIFE: How people live, occupations, lifestyle, community
            
            Write as an immersive world guide in 180-220 words.
            
            Background Description:
            """
        )
        
        if not self.llm:
            return self._generate_mock_background_description(genre)
        
        try:
            chain = background_template | self.llm | StrOutputParser()
            return chain.invoke({"story": story, "genre": genre}).strip()
        except Exception as e:
            logger.error(f"Error generating background description: {e}")
            return self._generate_mock_background_description(genre)
    
    def _generate_mock_character_description(self):
        """Fallback character description"""
        return """
        PHYSICAL APPEARANCE:
        Sarah Mitchell, 28, athletic 5'6" build with auburn hair and emerald eyes. 
        Small scar above left eyebrow, favors practical clothing and worn leather jacket.

        PERSONALITY & BACKGROUND:
        Insatiably curious with natural bravery that borders on recklessness. 
        Raised by grandmother (former librarian), developed love for books and mystery. 
        Quick-thinking and resourceful problem solver who dreams of grand adventures.

        MOTIVATIONS & SKILLS:
        Driven to discover hidden truths and experience real magic. Excellent research 
        abilities, keen observation, surprising problem-solving talents. Greatest fear 
        is living an ordinary life; deepest desire is finding magic in the world.
        """
    
    def _generate_mock_background_description(self, genre):
        """Fallback background description"""
        return f"""
        PHYSICAL ENVIRONMENT:
        Suburban reality intersects with magical realms through natural portals. 
        Mystical library features crystal spires, floating book islands, and 
        light-bridges defying physics.

        SOCIETY & CULTURE:
        Two-level world: mundane human society unaware of magic, and hidden magical 
        community governed by the Order of Keepers who maintain balance between dimensions.

        TIME & SYSTEMS:
        Contemporary setting blending modern technology with ancient magic. Library realm 
        exists outside normal time. Magic powered by imagination and collective storytelling.

        UNIQUE ELEMENTS:
        Stories are living entities capable of growth and reality influence. Library serves 
        as nexus where every imagined tale takes physical form. Gifted individuals can enter 
        narratives to guide outcomes and help lost stories find proper endings.
        """
    
    def _generate_mock_story(self, prompt, genre):
        """Fallback story generator"""
        return f"""
        Sarah discovered the mysterious oak tree in her backyard, shimmering with otherworldly 
        energy and etched with unknown symbols. When she touched its bark, the world shifted.

        She found herself in a vast magical library filled with floating books and glowing orbs. 
        An elderly woman with silver hair emerged from the towering bookshelves.

        "Welcome, Sarah. We've been waiting for you," the woman said. "You have the gift - 
        the ability to step between worlds and read the stories between reality's lines. 
        This library contains every story imagined and yet to be told."

        Books of every size floated gracefully, some open with self-turning pages, others 
        glowing with inner light. "Choose a story," the woman gestured. "Step inside it, 
        live it, and help it reach its proper ending. Some stories have lost their way."

        Sarah reached for a golden-glowing leather book. As she opened it, the world dissolved, 
        and she fell into a new adventure.

        Hours later, she returned home to find the oak tree gone, but carried the knowledge 
        that magic existed everywhere, waiting for those brave enough to seek it.
        """