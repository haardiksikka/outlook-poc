from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv


load_dotenv()

class DialogueAgent():
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.1)

    def dialogue(self, query: str, context: str) -> str:
        print(f"Query: {query}")
        system_prompt = """You are an expert at analyzing email conversations and client interactions.
        You have been provided with email chunks from a client conversation, each marked with [EMAIL-N] identifiers.
        
        IMPORTANT: When referencing information from specific emails, ALWAYS include the [EMAIL-N] citation.
        For example: "The client mentioned concerns about market volatility [EMAIL-2]" or "According to their latest update [EMAIL-5], they are considering..."
        
        Analyze these emails carefully and provide insightful responses to the user's questions.
        Focus on extracting key information, concerns, opportunities, and patterns.
        Include citations to specific emails whenever you reference information from them.

        Email chunks: {context}

        ---

        User Query: {query}

        Please analyze the emails and provide a comprehensive response to the query. 
        Remember to cite which emails [EMAIL-N] support your analysis."""

        prompt = ChatPromptTemplate.from_template(system_prompt)
        chain = prompt | self.llm | StrOutputParser()
        resp = chain.invoke({"context": context, "query": query})
        return resp