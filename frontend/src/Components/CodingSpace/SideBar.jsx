import React, {useContext} from "react";
import style from "./CodingSpace.module.css"
import {DraggableIconButton} from "../Icon/IconButton/IconButton.jsx";
import {BookText, Folder} from 'lucide-react'
import {CodingSpaceContext} from "../../Utility/CodingSpaceContext.jsx";
import {useDroppable} from "@dnd-kit/react";
import {panel} from "../../Utility/Enums.js";

export function SideBar({position}) {
    const {buttonsPos, panelPos, setPanelPos} = useContext(CodingSpaceContext)
    const {ref} = useDroppable({id: position})

    return <>
            <div
             ref={ref}
             className={style.sidebar}>
                <PanelToggle id={panel.tree} Icon={Folder}/>
                <PanelToggle id={panel.instruction} Icon={BookText}/>
            </div>
    </>

    function PanelToggle({id, Icon}) {
        return <>
            {buttonsPos[id] === position ?
                <DraggableIconButton id={id} Icon={Icon} onClick={() => {
                    setPanelPos(
                        {...panelPos, [position]: panelPos[position] === id ? panel.none : id}
                    )
                }}/> : <></>}
        </>
    }
}
