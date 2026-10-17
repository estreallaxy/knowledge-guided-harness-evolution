import os
import json
import argparse
import httpx
from openai import OpenAI
from tools import get_model_response, clean_json_response
from prompt.topic_tree_construction_prompt import topic_tree_prompt

exec(open("config.yaml").read())
class TopicTreeGenerator:
    def __init__(self, domain, examples, depth, width):
        self.domain = domain
        self.examples = examples
        self.depth = depth
        self.width = width
        self.topic_tree = {}
        self.output_file = f"topic_tree/{domain}_topic.jsonl"
        self.client = OpenAI(
            api_key=os.environ.get("GENERATION_API_KEY"),
            base_url=os.environ.get("GENERATION_BASE_URL"),
            http_client=httpx.Client(proxy=os.environ.get("HTTP_PROXY", ""))
        )
        os.makedirs("topic_tree", exist_ok=True)
    
    def generate_subtopics(self, parent_topic, examples):
        prompt = topic_tree_prompt.format(
            n=self.width,
            topic=parent_topic,
            Examples=examples
        )
        print(prompt)
        messages = [{"role": "system", "content": prompt}]
        
        while True:
            try:
                response = get_model_response(
                    self.client,
                    model_name="openai/gpt-4o-2024-11-20",
                    messages=messages,
                    temperature=0.7
                )
                
                result = clean_json_response(response)
                if "parent_topic" in result and "topics" in result:
                    return result["topics"]
                else:
                    print("Invalid response format, retrying...")
                    continue
            except Exception as e:
                print(f"Error generating subtopics: {e}")
                print("Retrying...")
                continue
    
    def get_user_input(self, prompt_text):
        """Get user input with prompt"""
        return input(prompt_text)
    
    def display_and_edit_topics(self, topics, parent_topic):
        """Display topics and allow user to edit them"""
        print(f"\nGenerated subtopics for '{parent_topic}':")
        print(", ".join(topics))
        
        print("\nYou can edit these topics. Press Enter to keep current topics, or type new topics separated by commas:")
        user_input = self.get_user_input("> ")
        
        if user_input.strip() == "":
            return topics
        else:
            # parse input
            edited_topics = [topic.strip() for topic in user_input.split(",") if topic.strip()]
            return edited_topics
    
    def save_to_jsonl(self, parent_topic, topics, current_depth):
        for topic in topics:
            entry = {
                "parent_topic": parent_topic,
                "topic": topic,
                "depth": current_depth,
                "domain": self.domain
            }

            with open(self.output_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")
            
            print(f"Saved: {topic} (depth {current_depth})")
    
    def build_topic_tree_recursive(self, parent_topic, current_depth, examples):
        if current_depth > self.depth:
            return
        
        print(f"\n{'='*50}")
        print(f"Processing: {parent_topic} (Depth: {current_depth}/{self.depth})")
        print(f"Examples: {examples}")
        print(f"{'='*50}")
        
        generated_topics = self.generate_subtopics(parent_topic, examples)
        
        final_topics = self.display_and_edit_topics(generated_topics, parent_topic)
        
        if current_depth == self.depth:
            self.save_to_jsonl(parent_topic, final_topics, current_depth)
            return
        
        for topic in final_topics:
            print(f"\nNow processing subtopic: {topic}")
            new_examples = self.get_user_input(f"Enter examples for '{topic}': ")
            
            if new_examples.strip():
                self.build_topic_tree_recursive(topic, current_depth + 1, new_examples)
            else:
                self.save_to_jsonl(parent_topic, [topic], current_depth)
    
    def generate(self):
        print(f"Starting topic tree generation for domain: {self.domain}")
        print(f"Depth: {self.depth}, Width: {self.width}")
        print(f"Initial examples: {self.examples}")
        print(f"Output file: {self.output_file}")
        
        self.build_topic_tree_recursive(self.domain, 1, self.examples)
        
        print(f"\nTopic tree generation completed!")
        print(f"Results saved to: {self.output_file}")

def main():
    parser = argparse.ArgumentParser(description="Interactive topic tree generation tool")
    parser.add_argument("--domain", type=str, required=True, 
                       help="Domain name (e.g., persuasion, recommendation)")
    parser.add_argument("--examples", type=str, required=True,
                       help="Initial examples for the domain")
    parser.add_argument("--depth", type=int, default=2,
                       help="Maximum depth of the topic tree")
    parser.add_argument("--width", type=int, default=2,
                       help="Number of subtopics to generate at each level")
    
    args = parser.parse_args()
    
    generator = TopicTreeGenerator(
        domain=args.domain,
        examples=args.examples,
        depth=args.depth,
        width=args.width
    )
    
    generator.generate()

if __name__ == "__main__":
    main()
