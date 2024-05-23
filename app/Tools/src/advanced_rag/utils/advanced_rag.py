import json
from langchain_community.vectorstores.chroma import Chroma


from Tools.src.advanced_rag.utils.prompt_utils import get_meta_filtration,get_reranker
from _temp.config import ChromaClient,PERSISTANT_DRIVE
from Tools.src.advanced_rag.utils.extraction_schema import RerankingSchema

# retrieving docs from the vector store 
def advanced_retrival(llm,meta_store,query,embeddings,chroma_client):
    filtration_chain=get_meta_filtration(llm)
    reranking_chain=get_reranker(llm)
    meta_filters=filtration_chain.invoke({"metastore":json.dumps(meta_store),"query":query})
    all_collections=eval(meta_filters.content) 
    print("filtered meta data --> ", meta_filters)
    context=""
    documents=[]
    for c in all_collections:
        cdb=Chroma(embedding_function=embeddings,persist_directory=PERSISTANT_DRIVE,client=chroma_client,collection_name=c)
        searcher=cdb.as_retriever(search_kwargs={"k":4})
        docs_searched=searcher.invoke(query)
        exception_flag=False
        for docs_ in docs_searched:
            ranking_out=reranking_chain.invoke({"context":docs_.page_content,"user_query":query,'schema':RerankingSchema.model_json_schema()})
            try:
                ranking=json.loads(ranking_out.content)
            except:
                exception_flag=True
            if exception_flag:
                try:
                    ranking=eval(ranking_out.content)
                except:
                    exception_flag=True
                if isinstance(ranking,dict):
                    exception_flag=False
            if exception_flag or 'rating' not in ranking:
                page_infomation=docs_.page_content
                page_infomation="## Metadata:"+json.dumps(docs_.metadata)+"  \n\n"+page_infomation
                context+=page_infomation
                docs_.page_content=page_infomation
                documents.append(docs_)
            else:
                rating=ranking['rating']
                if rating>2:
                    page_infomation=docs_.page_content
                    page_infomation="## Metadata:"+json.dumps(docs_.metadata)+"  \n\n"+page_infomation
                    context+=page_infomation
                    docs_.page_content=page_infomation
                    documents.append(docs_)
                    
    return documents
        