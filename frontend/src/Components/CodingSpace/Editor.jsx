import styles from "./CodingSpace.module.css"
import {useContext, useRef} from "react";
import {Editor as MonacoEditor} from "@monaco-editor/react"
import Label from "../Label/Label.jsx";
// import {tree} from "../../Utility/fakeAPI/files.js";
import {CodingSpaceContext} from "../../Utility/CodingSpaceContext.jsx";
import {IconComponent} from "../Icon/IconComponent.jsx";
import {XIcon} from "lucide-react";

export function Editor() {
    const {
        fileName,
        singleTab,
        tabs,
        selectFile,
        close,
        tree,
        setFiles
    } = useContext(CodingSpaceContext)
    const editorRef = useRef(null);
    const file = fileName !== null ? tree[fileName] : null;

    return <>
        <div className={styles.code}>
            <NavBar/>
            {fileName !== undefined ?
                (<MonacoEditor
                    theme="vs-dark"
                    path={file?.index ?? ''}
                    defaultLanguage={file?.language}
                    defaultValue={file?.content}
                    onMount={(editor) => (editorRef.current = editor)}
                    options={{
                        wordWrap: "on",
                    }}
                    onChange={(value) => {
                        setFiles(prev => 
                            prev.map(f => f.path === file.index ? {...f, content: value ?? ""} : f)
                        )
                    }}
                    />)
                : <div/>}
        </div>
    </>

    function NavBar() {

        return (
            <>
                <div className={styles.navBar}>
                    {
                        Object.values(tabs).map(e => (
                            <Tab status={fileName === e.index ? "selected" : "default"}
                                 fileIndex={e.index}
                                 fileName={e.data}/>
                        ))
                    }
                    {
                        singleTab !== null ? <Tab status={fileName === singleTab.index ? "selected" : "default"}
                                                  fileIndex={singleTab.index}
                                                  fileName={singleTab.data}
                                                  isSingle={true}/> : <></>
                    }
                </div>
            </>
        )
    }

    function Tab({fileName, fileIndex, status, isSingle = false}) {

        return (
            <>
                <div className={`${styles.tab} ${styles[status]} ${isSingle ? styles.single : ''}`} style={{}}>
                    <button
                        onClick={() => selectFile(fileIndex)}
                        className={styles.selectTabButton}
                    />
                    <div>
                        <Label text={fileName} size={'mini'}
                               className={`${styles.tabLabel} ${styles[status]} ${isSingle ? styles.single : ''}`}/>
                    </div>
                    <button
                        className={styles.closeTabButton}
                        onClick={() => close(fileIndex)}>
                        <IconComponent Icon={XIcon} className={styles.closeIcon}/>
                    </button>
                </div>

            </>
        )
    }
}

