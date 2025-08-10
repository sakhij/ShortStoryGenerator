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
        """Extract and describe the main character from the story in detail"""
        
        character_template = PromptTemplate(
            input_variables=["story"],
            template="""
            Based on this story: {story}
            
            Create a comprehensive character profile of the main protagonist including:
            
            PHYSICAL APPEARANCE:
            - Age, height, build, and overall physique
            - Hair color, style, and texture
            - Eye color and distinctive features
            - Clothing style and any notable accessories
            - Scars, tattoos, or unique physical markers
            
            PERSONALITY TRAITS:
            - Core personality characteristics
            - Strengths and positive qualities
            - Flaws and weaknesses
            - Quirks and mannerisms
            - How they interact with others
            
            BACKGROUND & HISTORY:
            - Where they grew up and family background
            - Education and life experiences
            - Previous jobs or roles
            - Significant events that shaped them
            
            MOTIVATIONS & GOALS:
            - What drives them forward
            - Their deepest desires and fears
            - Short-term and long-term objectives
            
            SKILLS & ABILITIES:
            - Special talents or abilities
            - Professional skills
            - Hobbies and interests
            - Areas where they excel or struggle
            
            Write this as a detailed character analysis in 150-200 words.
            
            Character Description:
            """
        )
        
        if self.llm is None:
            return self._generate_mock_character_description()
        
        try:
            chain = character_template | self.llm | StrOutputParser()
            description = chain.invoke({"story": story})
            return description.strip()
            
        except Exception as e:
            logger.error(f"Error generating character description: {e}")
            return self._generate_mock_character_description()
    
    def generate_background_description(self, story, genre):
        """Generate detailed background/setting description from the story"""
        
        background_template = PromptTemplate(
            input_variables=["story", "genre"],
            template="""
            Based on this {genre} story: {story}
            
            Create a rich and detailed description of the world and setting including:
            
            PHYSICAL ENVIRONMENT:
            - Geographic location and landscape
            - Climate and weather patterns  
            - Architecture and buildings
            - Natural features (mountains, rivers, forests, etc.)
            - Urban vs rural characteristics
            
            TIME PERIOD & HISTORICAL CONTEXT:
            - When the story takes place
            - Historical events that shaped this world
            - Level of technology or magic
            - Social and cultural evolution
            
            SOCIETY & CULTURE:
            - Social structure and class systems
            - Cultural norms and traditions
            - Languages spoken
            - Art, music, and entertainment
            - Religious or spiritual beliefs
            
            POLITICAL & ECONOMIC SYSTEMS:
            - Government structure and leadership
            - Laws and justice system
            - Economic systems and currency
            - Trade and commerce
            - Military or defense systems
            
            UNIQUE WORLD ELEMENTS:
            - What makes this world special or different
            - Magical systems, advanced technology, or supernatural elements
            - Mysterious locations or phenomena
            - Legends, myths, or important lore
            
            DAILY LIFE:
            - How ordinary people live
            - Common occupations and lifestyle
            - Food, housing, and transportation
            - Social gatherings and community events
            
            Write this as an immersive world guide in 180-220 words.
            
            Background Description:
            """
        )
        
        if self.llm is None:
            return self._generate_mock_background_description(genre)
        
        try:
            chain = background_template | self.llm | StrOutputParser()
            description = chain.invoke({"story": story, "genre": genre})
            return description.strip()
            
        except Exception as e:
            logger.error(f"Error generating background description: {e}")
            return self._generate_mock_background_description(genre)
    
    def _generate_mock_character_description(self):
        """Fallback detailed mock character description"""
        return """
        PHYSICAL APPEARANCE:
        Sarah Mitchell, 28 years old, stands 5'6" with an athletic yet graceful build developed through years of hiking and rock climbing. Her auburn hair falls in natural waves to her shoulders, often secured in a practical ponytail with loose strands framing her heart-shaped face. Bright emerald eyes sparkle with perpetual curiosity and intelligence, complemented by a small scar above her left eyebrow from a childhood adventure gone awry. She favors practical clothing - worn jeans, comfortable boots, and a weathered leather jacket that belonged to her grandmother.

        PERSONALITY & BACKGROUND:
        Sarah possesses an insatiable curiosity that often leads her into unexpected situations. Growing up in a small town with her grandmother, a former librarian and storyteller, she developed a deep love for books and mystery. Her natural bravery sometimes borders on recklessness, but her quick thinking and resourcefulness usually see her through challenges. She works as a research librarian but dreams of grand adventures beyond her quiet life.

        MOTIVATIONS & SKILLS:
        Driven by a desire to discover hidden truths and experience the magic she's read about in countless books, Sarah has developed excellent research skills, keen observational abilities, and surprising problem-solving talents. Her greatest fear is living an ordinary, unremarkable life, while her deepest desire is to find real magic in the world.
        """
    
    def _generate_mock_background_description(self, genre):
        """Fallback detailed mock background description"""
        return f"""
        PHYSICAL ENVIRONMENT:
        The story unfolds in a world where modern suburban reality intersects with ancient magical realms. Ordinary neighborhoods with tree-lined streets and colonial homes exist alongside mystical pocket dimensions accessible through natural portals. The magical library realm features impossibly vast spaces with soaring crystal spires, floating islands of books connected by bridges of pure light, and architecture that defies conventional physics.

        SOCIETY & CULTURE:
        This world operates on two levels - the mundane human society where most people live unaware of magic, and the hidden magical community governed by the ancient Order of Keepers. The Keepers maintain the balance between worlds, preserving stories and knowledge across dimensions. Magic users are rare, often discovering their abilities through chance encounters with mystical artifacts or locations.

        TIME PERIOD & SYSTEMS:
        Set in contemporary times, this world blends modern technology with ancient magical systems. The library realm exists outside normal time, where minutes can pass as hours in the real world. Magic is powered by imagination, belief, and the collective unconscious of all storytelling humanity.

        UNIQUE ELEMENTS:
        Stories themselves are living entities in this world, capable of growing, changing, and influencing reality. The library serves as a nexus where every tale ever imagined takes physical form, and gifted individuals can literally step into narratives to guide their outcomes and help lost stories find their proper endings.
        """
    
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