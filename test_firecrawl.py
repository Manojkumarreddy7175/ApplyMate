import asyncio
import os
from langchain_google_genai import ChatGoogleGenerativeAI
from mcp_use import MCPAgent, MCPClient

async def test_firecrawl():
    from dotenv import load_dotenv
    load_dotenv()

    client = MCPClient.from_config_file("mcp_config.json")
    os.environ["GOOGLE_API_KEY"] = os.getenv("GEMINI_API_KEY")
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        temperature=0.1
    )

    agent = MCPAgent(llm=llm, client=client, max_steps=50, verbose=True)

    # Test search
    try:
        prompt = "Use firecrawl_search to search for 'software engineer jobs remote' with limit 5 and sources web."
        result = await agent.run(prompt)
        print("Search test result:")
        print(result)

        # Test scrape
        prompt2 = "Use firecrawl_scrape to scrape https://www.google.com with format markdown."
        result2 = await agent.run(prompt2)
        print("Scrape test result:")
        print(result2[:500])
    except Exception as e:
        print(f"Test failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_firecrawl())
