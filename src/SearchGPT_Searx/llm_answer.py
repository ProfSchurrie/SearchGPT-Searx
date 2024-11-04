from SearchGPT_Searx.fetch_web_content import WebContentFetcher
from SearchGPT_Searx.retrieval import EmbeddingRetriever
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.schema import HumanMessage
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler


class GPTAnswer:
    TOP_K = 10  # Top K documents to retrieve
    TEMPLATE = """
        Web search result:
        {context_str}

        Instructions: You are a/an {profile}. Using the provided web search results, write a comprehensive and detailed reply to the given query. 
        Make sure to cite results using [number] notation after the reference.
        At the end of the answer, list the corresponding references with indexes, each reference contains the URLs and quoted sentences from the web search results by the order you marked in the answer above and these sentences should be exactly the same as in the web search results.
        Here is an example of a reference:
            [1] URL: https://www.pocketgamer.biz/news/81670/tencent-and-netease-dominated-among-chinas-top-developers-in-q1/
                Quoted sentence: Tencent accounted for roughly 50% of domestic market revenue for the quarter, compared to 40% in Q1 2022.

        Answer in language: {language}
        Query: {query}
        Output Format: {format}
        Please organize your output according to the Output Format. If the Output Format is empty, you can ignore it.
        """

    def _format_reference(self, relevant_docs_list, link_list):
        # Format the references from the retrieved documents for use in the prompt
        reference_url_list = [(relevant_docs_list[i].metadata)['url'] for i in range(self.TOP_K)]
        reference_content_list = [relevant_docs_list[i].page_content for i in range(self.TOP_K)]
        reference_index_list = [link_list.index(link)+1 for link in reference_url_list]
        rearranged_index_list = self._rearrange_index(reference_index_list)

        # Create a formatted string of references
        formatted_reference = "\n"
        for i in range(self.TOP_K):
            formatted_reference += ('Webpage[' + str(rearranged_index_list[i]) + '], url: ' + reference_url_list[i] + ':\n' + reference_content_list[i] + '\n\n\n')
        return formatted_reference

    def _rearrange_index(self, original_index_list):
        # Rearrange indices to ensure they are unique and sequential
        index_dict = {}
        rearranged_index_list = []
        for index in original_index_list:
            if index not in index_dict:
                index_dict.update({index: len(index_dict) + 1})
                rearranged_index_list.append(len(index_dict))
            else:
                rearranged_index_list.append(index_dict[index])
        return rearranged_index_list

    def get_answer(self, query, relevant_docs, language, output_format, profile, model_name: str, api_key: str):
        # Create an instance of ChatOpenAI and generate an answer
        llm = ChatOpenAI(model_name=model_name, openai_api_key=api_key, temperature=0.0, streaming=True,
                         callbacks=[StreamingStdOutCallbackHandler()])

        prompt_template = PromptTemplate(
            input_variables=["profile", "context_str", "language", "query", "format"],
            template=self.TEMPLATE
        )

        profile = "conscientious researcher" if not profile else profile
        summary_prompt = prompt_template.format(context_str=relevant_docs, language=language, query=query,
                                                format=output_format, profile=profile)
        print("\n\nThe message sent to LLM:\n", summary_prompt)
        print("\n\n", "=" * 30, "GPT's Answer: ", "=" * 30, "\n")
        gpt_answer = llm([HumanMessage(content=summary_prompt)])

        return gpt_answer
