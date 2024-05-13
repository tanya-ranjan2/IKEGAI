import fitz 
import pandas as pd
from langchain_core.documents.base import Document
import os
import shutil
from ultralyticsplus import YOLO, render_result
from PIL import Image
import io

def convert_to_langchain_docs(docs):
    document_format=[]
    for doc in docs:
        document_format.append(Document(page_content=doc['block'],metadata={"page":doc['page_no'],"path":doc['doc_name']}))
    return document_format

def process(pdf_path:str):
    doc=fitz.open(pdf_path)
    return extract_doc(doc, pdf_path)

def get_data(docs,page:int=None,page_range:list=None):
    if page:
        page_docs=[]
        for doc in docs:
            if doc['page_no']==page:
                page_docs.append(doc)
        return page_docs
    if page_range:
        page_list=list(range(page_range[0],page_range[1]))
        page_docs=[]
        for doc in docs:
            if doc['page_no'] in page_list:
                page_docs.append(doc)
        return page_docs
    
    return docs
 
def extract_doc(docs,doc_name:str,clean:bool=True):
    data_format:list=[]
    clean_list:list=["\n"]
    for page_no in range(docs.page_count):
        para:list=[]
        last_para:str=""
        starts_with:tuple=('',"(","•","¾")
        merge_next:bool=False
        merge_next_char:str=""
        for b in docs[page_no].get_text("blocks"):
            x0,y0,x1,y1,text,block_id,block_type=b
            if clean:
                for c in clean_list:
                    text=text.replace(c,"")
                    text=text.strip()
            if text.strip()=="":
                continue
            if merge_next:
                if len(para)==0:
                    para.append("")
                para[-1]=last_para+text
                last_para+=text
                op,character=merge_next_char.split("_")
                if op=="HAS":
                    if character in text:
                        merge_next=False
                        merge_next_char=""
                elif op=="ENDS":
                    if text.strip().endswith(character):
                        merge_next=False
                        merge_next_char=""
                continue

            if "(" in text and ")" not in text:
                merge_next_char="HAS_)"
                merge_next=True
            elif "[" in text and "]" not in text:
                merge_next_char="HAS_]"
                merge_next=True
            elif "{" in text and "}" not in text:
                merge_next_char="HAS_}"
                merge_next=True
            if text.startswith(starts_with):
                if len(para)==0:
                    para.append("")
                para[-1]=last_para+text
                last_para+=text
                continue
            if not text.strip().endswith("."):
                merge_next=True
                merge_next_char="ENDS_."
            elif text.strip()[0].islower():
                
                if len(para)==0:
                    para.append("")
                para[-1]=last_para+text
                last_para+=text
                continue

            para.append(text)
            last_para=text
            
        for p in para:
            data_format.append({
                "doc_name":doc_name,
                "page_no":page_no,
                "block":p
            })
    return data_format



def check_if_scanned(page: str,threshold:float=0.05) -> tuple:
    """
    Calculate the percentage of document that is covered by (searchable) text.

    If the returned percentage of text is very low, the document is
    most likely a scanned PDF
    """
    total_page_area = 0.0
    total_text_area = 0.0

    
    total_page_area = total_page_area + abs(page.rect)
    text_area = 0.0
    for b in page.get_text_blocks():
        x0,y0,x1,y1,text,block_id,block_type=b
        if not text.startswith("<image"):
            r = fitz.Rect(b[x0,y0,x1,y1])  # rectangle where block text appears
            text_area = text_area + abs(r)
    total_text_area = total_text_area + text_area
    text_perc=total_text_area / total_page_area
    return text_perc < threshold, text_perc
def check_if_scanned_full_doc(path: str,threshold=0.05) -> float:
    """
    Calculate the percentage of document that is covered by (searchable) text.

    If the returned percentage of text is very low, the document is
    most likely a scanned PDF
    """
    total_page_area = 0.0
    total_text_area = 0.0
    
    doc = fitz.open(path)

    for page_num, page in enumerate(doc):
        total_page_area = total_page_area + abs(page.rect)
        text_area = 0.0
        for b in page.get_text_blocks():
            x0,y0,x1,y1,text,block_id,block_type=b
            if not text.startswith("<image"):
                r = fitz.Rect(b[:4])  # rectangle where block text appears
                text_area = text_area + abs(r)
        total_text_area = total_text_area + text_area
    doc.close()
    text_perc=total_text_area / total_page_area
    return text_perc < threshold, text_perc

def convert_to_doc_intell_pdf_format(pdf_file:str,pages=None,out_dir="temp"):
    doc1 = fitz.open(pdf_file)
    if not os.path.exists(out_dir):
        os.mkdir(out_dir)
    else:
        shutil.rmtree(out_dir)
        os.mkdir(out_dir)
    # Create a new empty PDF document
    filenames=[]
    if pages is None:
        # Insert the first 2 pages of doc1 into doc2
        for p in range(len(doc1)):
            doc2 = fitz.open()
            doc2.insert_pdf(doc1, to_page=p+1,from_page=p)
            
            # Save the modified document as "first-and-last-10.pdf"
            fname=f"{out_dir}/_temp_pdf_{p}.pdf"
            doc2.save(fname)
            filenames.append(fname)
            
            
    ## Implement if pages are given
    
    return filenames

def check_if_hasTables(pdf_path: str, model_name: str = 'keremberke/yolov8m-table-extraction') -> list:
    """
    Args -
        pdf_path: str = path of the pdf file
        model_name: str = Default - YOLO v8 to detect tables
    Returns - 
        List containing binary values 0, 1. 0 indicating absence of tables and 1 indicating presence of table. 
    """

    hasTables = []
    # YOLO model
    yolo_model = YOLO(model_name)
    yolo_model.overrides['conf'] = 0.25 # NMS confidence threshold
    yolo_model.overrides['iou'] = 0.45  # NMS IoU threshold
    yolo_model.overrides['agnostic_nms'] = False  # NMS class-agnostic
    yolo_model.overrides['max_det'] = 1000  # maximum number of detections per image

    pdf_doc = fitz.open(pdf_path)
    for page_no in range(pdf_doc.page_count):
        page = pdf_doc.load_page(page_no)
        page_image = page.get_pixmap()
        page_data = page_image.pil_tobytes('ppm') # PIL bytes
        results = yolo_model.predict(Image.open(io.BytesIO(page_data)))
        hasTables.append(0) if len(results[0].boxes.conf) == 0 else hasTables.append(1)
    
    pdf_doc.close()

    return hasTables

def extract_doc_page(docs, page_no: int ,doc_name: str ,clean:bool=True):
    """
    Extracts text from pdf page. Utilised on pages without tables.
    Args -
        docs: fitz.open(pdf_path)
        page_no: int - page number for which text needs to be extracted
        doc_name: str - name of the document 
        clean: bool
    Returns -
        List of dictionaries containing block (content), page_no and doc_name data. 
    """

    data_format:list=[]
    clean_list:list=["\n"]

    para:list=[]
    last_para:str=""
    starts_with:tuple=('',"(","•","¾")
    merge_next:bool=False
    merge_next_char:str=""
    for b in docs[page_no].get_text("blocks"):
        x0,y0,x1,y1,text,block_id,block_type=b
        if clean:
            for c in clean_list:
                text=text.replace(c,"")
                text=text.strip()
        if text.strip()=="":
            continue
        if merge_next:
            if len(para)==0:
                para.append("")
            para[-1]=last_para+text
            last_para+=text
            op,character=merge_next_char.split("_")
            if op=="HAS":
                if character in text:
                    merge_next=False
                    merge_next_char=""
            elif op=="ENDS":
                if text.strip().endswith(character):
                    merge_next=False
                    merge_next_char=""
            continue

        if "(" in text and ")" not in text:
            merge_next_char="HAS_)"
            merge_next=True
        elif "[" in text and "]" not in text:
            merge_next_char="HAS_]"
            merge_next=True
        elif "{" in text and "}" not in text:
            merge_next_char="HAS_}"
            merge_next=True
        if text.startswith(starts_with):
            if len(para)==0:
                para.append("")
            para[-1]=last_para+text
            last_para+=text
            continue
        if not text.strip().endswith("."):
            merge_next=True
            merge_next_char="ENDS_."
        elif text.strip()[0].islower():
            
            if len(para)==0:
                para.append("")
            para[-1]=last_para+text
            last_para+=text
            continue

        para.append(text)
        last_para=text
        
    for p in para:
        data_format.append({
            "doc_name":doc_name,
            "page_no":page_no + 1,
            "block":p
        })

    return data_format

def table_to_dataframe(page_paras, replace: bool = True) -> pd.DataFrame :
    """
    Converts DocumentTable Object to Pandas DataFrame
    Args -
        page_paras : Azure Doc intell DocumentTableObject. 
        replace: bool = If True replaces NULL columns names with Column1, Column2, etc...
    Returns -
        DataFrame 
    """
    max_column_row_span = max([cell.row_span if cell.kind == 'columnHeader' else 0 for cell in page_paras.cells])
    main_data = [[np.nan]*page_paras.column_count for i in range(page_paras.row_count-max_column_row_span)]
    columns = [None]*page_paras.column_count
    for cell in page_paras.cells :
        if cell.kind == 'columnHeader' :
            row_index, column_index = cell.row_index, cell.column_index
            for i in range(cell.row_span) :
                for j in range(cell.column_span) :  
                    if columns[column_index+j] :
                        columns[column_index+j] += ' ' + str(cell.content )
                    else :
                        columns[column_index+j] = str(cell.content)
        elif cell.kind == "content" :  
            row_index, column_index = cell.row_index, cell.column_index
            if row_index == 21 :
                print(cell.content, cell)
            for i in range(cell.row_span) :
                for j in range(cell.column_span) :
                    main_data[row_index+i-max_column_row_span][column_index+j] = cell.content
 
    # replace NULL column names with column1, column2, ...
    if replace :
        pointer = 0
        for i in range(len(columns)) :
            if not columns[i] :
                columns[i] = 'column'+str(pointer)
                pointer += 1  
               
    df = pd.DataFrame(main_data, columns= columns)
 
    return df