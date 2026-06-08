import {useContext, useRef} from "react";
import {CodingSpaceContext} from "../../Utility/CodingSpaceContext.jsx";
import {ControlledTreeEnvironment, InteractionMode, Tree} from "react-complex-tree";
import styles from "./CodingSpace.module.css"
import {tree} from "../../Utility/fakeAPI/files.js";

export function FileTree() {
    const treeEnvRef = useRef(null);
    const {
        selectedItems,
            setSelectedItems,
            focusItem,
            primaryAction,
            treeRef, expandedItems, setExpandedItems, focusedItem
    } = useContext(CodingSpaceContext)


    return <>
        <div className={styles.tree}>
            <ControlledTreeEnvironment
                getItemTitle={item => item.data}
                viewState={{
                    ['tree-2']: {
                        focusedItem,
                        expandedItems,
                        selectedItems,
                    },
                }}
                defaultInteractionMode={InteractionMode.DoubleClickItemToExpand}
                canDragAndDrop={false}
                canDropOnFolder={false}
                canReorderItems={false}
                disableMultiselect={true}
                onSelectItems={items => setSelectedItems(items)}
                onFocusItem={(item) => focusItem(item)}
                onPrimaryAction={(item) => primaryAction(item)}
                onExpandItem={item => setExpandedItems([...expandedItems, item.index])}
                onCollapseItem={item =>
                    setExpandedItems(expandedItems.filter(expandedItemIndex => expandedItemIndex !== item.index))
                }
                ref={treeEnvRef}
                items={tree}>
                <Tree treeId="tree-2" rootItem="root" treeLabel="Tree Example" ref={treeRef}/>
            </ControlledTreeEnvironment>
        </div>
    </>
}