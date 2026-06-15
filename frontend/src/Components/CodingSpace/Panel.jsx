import React, {useContext, useEffect, useRef, useState} from "react";
import {CodingSpaceContext} from "../../Utility/CodingSpaceContext.jsx";
import {bar, panel} from "../../Utility/Enums.js";
import {Instructions} from "./Instructions.jsx";
import {Results} from "./Results.jsx"
import {FileTree} from "./FileTree.jsx";
import style from "./CodingSpace.module.css";

export function Panel({position}) {
    const {panelPos} = useContext(CodingSpaceContext)

    const [expandedWidth, setExpandedWidth] = useState(250);
    const collapsed = panelPos[position] === panel.none
    const width = collapsed ? 0 : expandedWidth;
    const [activeResizer, setActiveResizer] = useState(false);
    const startPosRef = useRef({ x: 0, width: 0 });

    const handleMouseDown = (e) => {
        e.preventDefault();
        setActiveResizer(true);
        startPosRef.current = {
            x: e.clientX,
            width: expandedWidth,
        };

    };

    useEffect(() => {
        const handleMouseMove = (e) => {
            if (!activeResizer) return;

            const bodyWidth = document.body.clientWidth

            const deltaX = (position === bar.right ? -1 : 1) * (e.clientX - startPosRef.current.x);

            let newWidth = startPosRef.current.width + deltaX;

            const max = bodyWidth * 0.2;
            const min = bodyWidth * 0.1;

            newWidth = Math.min(Math.max(newWidth, min), max);
            setExpandedWidth(newWidth);
        };

        const handleMouseUp = () => {
            setActiveResizer(false);
        };

        if (activeResizer) {
            window.addEventListener('mousemove', handleMouseMove);
            window.addEventListener('mouseup', handleMouseUp);
            document.body.style.cursor = "col-resize";
        }

        return () => {
            window.removeEventListener('mousemove', handleMouseMove);
            window.removeEventListener('mouseup', handleMouseUp);
            document.body.style.cursor = "default";
        };
    }, [activeResizer, width]);

    const resizer = <div
        className={`${style.resizer} ${position === bar.left ? style.left : style.right}`}
        onMouseDown={(e) => handleMouseDown(e)}
    />

    return <>
        <div id={position}
            style={{
                width: width,
                position: 'relative',
            }}
        >
            {
                panelPos[position] === panel.tree ? <FileTree/> :
                panelPos[position] === panel.instruction ? <Instructions/> :
                panelPos[position] === panel.results ? <Results/> :
                null
            }
            {!collapsed && resizer}
        </div>

    </>
}