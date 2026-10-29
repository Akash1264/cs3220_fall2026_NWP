# Import dependencies
import streamlit as st
import streamlit.components.v1 as components #to display the HTML code
from streamlit_image_coordinates import streamlit_image_coordinates
#pip install streamlit-image-coordinates

#from st_image_button import st_image_button

import networkx as nx #Networkx for creating graph data
from pyvis.network import Network #to create the graph as an interactive html object
from PIL import Image


from src.CSPclass import CSPBasic
from src.algorithms import AC3

nodeColors={
    "empty":"white",
    "filled": "yellow"
}

imgCell={
    "1": "imgs/1.png",
    "3":"imgs/3.png",
    "9":"imgs/9.png",
    "empty":"imgs/empty.png"
}





def main():
    if "clicked" not in st.session_state:
        st.session_state["clicked"] = False
        
    tab1, tab2 = st.tabs(["Initial Sudoku", "Graph of constraints"])
    
    
    sudokuNeighbors,sudokuDomains,sudokuConstraints1=getSudokuData()        
    basicSudokuCSP=CSPBasic(variables=sudokuNeighbors.keys(),neighbors=sudokuNeighbors, domains=sudokuDomains, constraints=sudokuConstraints1)
    ac3=False
    
    if not st.session_state["clicked"]:        
        if st.button("Run AC-3"):
            st.session_state["clicked"]=True
            AC3(basicSudokuCSP)
            ac3=True
            
            
        
    
    with tab1:
        st.header("CSP: Simple Sudoku Example")
        
        # Define the number of rows you want
        num_rows = 3
        # Define the number of columns per row
        columns_per_row = 3
        vars=list(basicSudokuCSP.variables)
        print(vars)
        activeCell=None        

        
        j=0
        for i in range(num_rows):
            # Create a set of columns for each row
            cols = st.columns(columns_per_row)
            
            # Place elements within each column of the current row
            #img = Image.open("images/top_spiderman.png")
            #st.button(st.image(img))
            
            for col_index, col in enumerate(cols):
                with col:
                    options=basicSudokuCSP.domains[vars[j]]
                    if len(options)==1:
                        val=options[0]
                        print(val, imgCell[str(val)])
                        st.image(imgCell[str(val)], caption=f"filled_cell_{vars[j]}")
                        #value = streamlit_image_coordinates(imgCell[str(val)], key=f"button_{vars[j]}")
                        #if value!=None:
                            #activeCell=vars[j]
                            #print(activeCell)
                            #st.text(activeCell)


                        #st_image_button(f"{vars[j]}",imgCell[str(val)] , key=f"button_{vars[j]}")
                        #img = Image.open(imgCell[str(val)])
                        #st.button("",icon=imgCell[str(val)])
                            #st.session_state.last_click = vars[j]
                                         
                        #if st_image_button(f"{vars[j]}",imgCell[str(val)] , key=f"button_{vars[j]}"):
                            #st.session_state.last_click = vars[j]
                    else:
                        val="empty"
                        print(val, imgCell[val])
                        #st.image(imgCell[str(val)], caption=f"empty_cell_{vars[j]}")
                        value = streamlit_image_coordinates(imgCell[str(val)], key=f"button_{vars[j]}")
                        if value!=None:
                            activeCell=vars[j]
                            if ac3:
                                strList=[str(i) for i in basicSudokuCSP.curr_domains[activeCell]]
                                st.write(strList)
                            else:
                                strList=[str(i) for i in basicSudokuCSP.domains[activeCell]]
                                st.write(strList)



                        #st_image_button(f"{vars[j]}",imgCell[val] , key=f"button_{vars[j]}")
                        #img = Image.open(imgCell[val])
                        #st.button("", icon=imgCell[val])
                            #st.session_state.last_click = vars[j]
                        
                        #print(val, imgCell[str(val)])     
                        #if st_image_button(f"{vars[j]}",imgCell[val] , key=f"button_{vars[j]}"):
                            #st.session_state.last_click = vars[j]
                j+=1
        #st.text(activeCell)
        #st.write(f"The current domain of the active cell: {basicSudokuCSP.curr_domains[activeCell]}")

        # Display the coordinates of the last clicked cell
        #if 'last_click' in st.session_state:
            #st.write(f"You clicked cell: {st.session_state.last_click}")
            
        
    with tab2:
        
        buildGraph(basicSudokuCSP, nodeColors)
        
        if ac3:
            st.success("AC-3 applied. Check new domains")
            buildGraph(basicSudokuCSP, nodeColors, ac3)
        
 
            
        
        #st.button("Run AC-3", on_click= , args= [option])
        
         

        
def getSudokuData():
    var1=list("ABC")
    var2=range(1,4)
    filled={'A3':3, 'B1':9,'C3':1}

    vars=set()

    for letter in var1:
        for number in var2:
            vars.add(letter+str(number))
            sudokuNeighbors={}

    for letter in var1:
        for number in var2:
            sudokuNeighbors[letter+str(number)]=[]
            
    for key1 in sudokuNeighbors.keys():
        for key2 in sudokuNeighbors.keys():
            if key1!=key2:
                sudokuNeighbors[key1].append(key2)
            
    sudokuDomains={var:[filled[var]] if var in filled else [ch for ch in range(1,10)] for var in sudokuNeighbors.keys()}
    sudokuConstraints1 = lambda X, x, Y, y: x!=y
    
    return sudokuNeighbors,sudokuDomains,sudokuConstraints1

        
        
        
def buildGraph(SudokuCSP, nodeColors, ac3=False):
    netSudoku= Network(
                bgcolor ="#242020",
                font_color = "white",
                height = "750px",
                width = "100%"
                ) 
    
    nodeColorsDict={}
    nodeTitlesDict={}
    nodeLabelsDict={}
    nodes=list(SudokuCSP.variables)

    for node in nodes:
        if len(SudokuCSP.domains[node])==1:
            nodeColorsDict.setdefault(node,nodeColors["filled"])
            if ac3:
                nodeTitlesDict.setdefault(node,str(SudokuCSP.curr_domains[node][0]))
            else:
                nodeTitlesDict.setdefault(node,str(SudokuCSP.domains[node][0]))
            nodeLabelsDict.setdefault(node,str(SudokuCSP.domains[node][0]))           
        else:
            nodeColorsDict.setdefault(node,nodeColors["empty"])
            if ac3:
                string_list = [str(i) for i in SudokuCSP.curr_domains[node]]
               
            else:
                string_list = [str(i) for i in SudokuCSP.domains[node]]
            nodeTitlesDict.setdefault(node, ",".join(string_list) )
                
            nodeLabelsDict.setdefault(node,"")      
           
            
    x_coords = {}
    y_coords = {}

    for node in nodes:
        if node[0].lower()=="a":
            y_coords.setdefault(node,50)            
        elif node[0].lower()=="b":
            y_coords.setdefault(node,100)
        elif node[0].lower()=="c":
            y_coords.setdefault(node,150)
        x_coords.setdefault(node,int(node[1])*50)
           
            
    
    # initialize graph
    g = nx.Graph()
    
    # add the nodes
    for node in nodes:
        g.add_node(node, color=nodeColorsDict[node], size=10, title=nodeTitlesDict[node], label=nodeLabelsDict[node],  x_coord=x_coords[node],y_coord=y_coords[node])

    # add the edges
    print(SudokuCSP.neighbors)
    
    
    for nodeFrom in SudokuCSP.neighbors.keys():
        for nodeTo in SudokuCSP.neighbors[nodeFrom]:        
            if nodeFrom[0]==nodeTo[0]: # row const-s
                g.add_edge(nodeFrom,nodeTo, color="red")
            elif nodeFrom[1]==nodeTo[1]: # col const-s
                g.add_edge(nodeFrom,nodeTo, color="blue")
            else:
                g.add_edge(nodeFrom,nodeTo, color="green") # diag con-s
            
    print(g.edges)
    # generate the graph
    netSudoku.from_nx(g)
    #netSudoku.toggle_physics(False)
    
    netSudoku.save_graph('L6_SimpleSudoku.html')
    HtmlFile = open(f'L6_SimpleSudoku.html', 'r', encoding='utf-8')
    components.html(HtmlFile.read(), height = 1200,width=1000)
    
    
    
    
if __name__ == '__main__':
    main()
        