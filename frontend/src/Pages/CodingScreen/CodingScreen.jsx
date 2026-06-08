import React, {useRef, useState} from "react";
import 'react-complex-tree/lib/style-modern.css';
import styles from './CodingScreen.module.css'
import TopBar from "../../Components/TopBar/TopBar.jsx";
import {useParams} from "react-router-dom";
import {CodingSpaceContext} from "../../Utility/CodingSpaceContext.jsx";
import {DragDropProvider} from "@dnd-kit/react";
import {bar, panel} from "../../Utility/Enums.js";
import {SideBar} from "../../Components/CodingSpace/SideBar.jsx";
import {Panel} from "../../Components/CodingSpace/Panel.jsx";
import {Editor} from "../../Components/CodingSpace/Editor.jsx";

export function CodingScreen() {
    const treeRef = useRef(null)
    const [fileName, setFileName] = useState(undefined);
    const [tabs, setTabs] = useState([])
    const [singleTab, setSingleTab] = useState(null);
    const [selectedItems, setSelectedItems] = useState([]);
    const [expandedItems, setExpandedItems] = useState([]);
    const [focusedItem, setFocusedItem] = useState('root');
    const {topic, id} = useParams()
    const [buttonsPos, setButtonsPos] = useState({[panel.tree]: bar.left, [panel.instruction]: bar.right})
    const [panelPos, setPanelPos] = useState({[bar.left]: panel.tree, [bar.right]: panel.instruction});

    function focusItem(item) {
        if (item.isFolder) {
            return
        }
        setFocusedItem(item.index)
        if (tabs.includes(item)) {
            primaryAction(item)
            return
        }
        setSingleTab(item)
        setFileName(item.index.toString())
    }

    function primaryAction(item) {
        if (!tabs.includes(item))
            setTabs([...tabs, item])
        if (singleTab === item)
            setSingleTab(null)
        setFileName(item.index.toString())
    }

    function selectFile(index) {
        if (index !== undefined) {
            if (treeRef.current !== null) {
                treeRef.current.focusItem(index)
                treeRef.current.selectItems([index]);
            }
            setFileName(index.toString())
            setFocusedItem(index);
            setSelectedItems([index]);
        } else {
            setSelectedItems(null)
        }
    }

    function close(index) {
        if (index === singleTab?.index) {
            setSingleTab(null);
        }
        const newTabs = tabs.filter(i => i.index !== index)
        setTabs(newTabs)
        setFileName(newTabs[0]?.index?.toString())
        selectFile(newTabs[0]?.index?.toString())
    }

    // useEffect(() => {
    //     editorRef.current?.focus();
    // }, [file?.name]);


    return (
        <>

            <TopBar small={true} topic={topic}/>
            <section className={styles.pageBackground}>
                <CodingSpaceContext.Provider
                    value={{
                        selectedItems,
                        setSelectedItems,
                        fileName,
                        setFileName,
                        singleTab,
                        setSingleTab,
                        tabs,
                        setTabs,
                        treeRef,
                        buttonsPos,
                        setButtonsPos,
                        panelPos,
                        setPanelPos,
                        expandedItems,
                        setExpandedItems,
                        focusedItem,
                        setFocusedItem,
                        focusItem,
                        primaryAction,
                        selectFile,
                        close
                    }}>
                    <DragDropProvider
                        onDragEnd={(event) => {
                            const target = event.operation.target
                            const source = event.operation.source
                            if (!target) return
                            setPanelPos((prev) => {
                                const curBar = Object.keys(prev).find(key => prev[key] === source.id);
                                if (curBar !== undefined) {
                                    return {...prev, [curBar]: panel.none, [target.id]: source.id};
                                }
                                return prev;
                            })
                            setButtonsPos({...buttonsPos, [source?.id]: target?.id});
                        }}>
                        <div className={styles.layout}>
                            <SideBar position={bar.left}/>
                            <Panel position={bar.left}/>
                            <Editor/>
                            <Panel position={bar.right}/>
                            <SideBar position={bar.right}/>
                        </div>

                    </DragDropProvider>
                </CodingSpaceContext.Provider>
            </section>
        </>
    );
}