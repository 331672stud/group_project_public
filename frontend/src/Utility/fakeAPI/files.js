const indexHTML = `<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <link rel="icon" type="image/svg+xml" href="/vite.svg" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>reactapp</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.jsx"></script>
  </body>
</html>
`
const AppJS = `import './App.css'

function App() {
    return <>
    </>
}

export default App
`
const AppCSS = `.grid {
    display: grid;
    grid-template-columns: auto auto auto;
    width: 0;
}

.grid > div {
    margin: 10px;
}`
const LabelJS = `import styles from "./Label.module.css"

function Label({className, text, size, weight, color}) {
    return (
        <>
            <p className={\`\${styles.p} 
                           \${styles[size]} 
                           \${styles[weight]} 
                           \${styles[color]} 
                           \${className}\`}>
                {text}
            </p>
        </>
    )
}

export default Label`
const LabelCSS = `
.p {
    font-family: var(--main-font), sans-serif;
    color: var(--stroke-color);
    margin: 0;
}

    .p.mini {
        font-size: var(--font-mini);
        height: var(--font-mini);
    }

    .p.small {
        font-size: var(--font-small);
        height: var(--font-small);
    }

    .p.medium {
        font-size: var(--font-medium);
        height: var(--font-medium);
    }

    .p.large {
        font-size: var(--font-large);
        height: var(--font-large);
    }

    .p.bold {
        font-weight: bold;
    }

    .p.stroke {
        color: var(--stroke-color);
    }

    .p.strokeGray {
        color: var(--stroke-gray-color)
    }`
const TopicJS = `import styles from "./TopicPanel.module.css"
import Label from "../Label/Label.jsx";
import {BookOpenText} from "lucide-react";
import {NotebookPen} from "lucide-react"

function TopicPanel({topic}) {
    return (
        <>
            <div className={styles.component}>
                <div className={styles.header}>
                    <Label className={styles.title} size={"large"} text={topic.name}/>
                </div>
                <div className={styles.body}>
                    <div className={styles.iconsContainer}>
                        <BookOpenText className={styles.icon}/>
                        <NotebookPen className={styles.icon}/>
                    </div>
                    <div className={styles.progressBarContainer}>
                        <ProgresBar color={'theory'} completion={topic.theoryCompletion}/>
                        <ProgresBar color={'easy'} completion={topic.easyCompletion}/>
                        <ProgresBar color={'medium'} completion={topic.mediumCompletion}/>
                        <ProgresBar color={'hard'} completion={topic.hardCompletion}/>
                    </div>
                </div>
            </div>
        </>
    )
}

function ProgresBar({color, completion}) {

    const label = color.charAt(0).toUpperCase() + color.slice(1)
    const [done, all] = completion.split('/')
    const percentage = 100*done/all
    return (
        <>

            <div className={styles.progressBar}>
                <div className={styles.barTitle}><Label text={label} size={'small'}/></div>
                <div className={styles.barBackground}>
                    <div className={\`\${styles.barProgres} \${styles[color]}\`} style={{right: 100-percentage + '%'}}/>
                </div>
                <div className={styles.barNum}><Label text={completion} size={'small'}/></div>

            </div>

        </>
    )
}

export default TopicPanel`
const TopicCSS = `:root {
    --bar-height: 10px;
}

.header {
    background-color: var(--common-color);
    height: 25%;
    position: relative;
    /*z-index: -1;*/
    border-radius: 17px 17px 0 0;
    box-shadow: -4px 4px 4px -2px rgb(0,0,0,0.25) inset;
}

.body {
    background-color: var(--strong-color);
    height: 75%;
    position: relative;
    /*z-index: -1;*/
    overflow: hidden;
    box-shadow: -4px 0 4px -2px rgb(0,0,0,0.25) inset;
    border-radius: 0 0 17px 17px;
}

.component {
    width: 330px;
    height: 200px;
    /*box-shadow: -4px 4px 4px rgb(0,0,0,0.25) inset;*/
    border-radius: 17px;
    overflow: hidden;
    border-style: solid;
    border-color: rgb(0,0,0,0);
}

.iconsContainer {
    height: 100%;
    width: 30%;
    float: left;
}

.icon {

    border-style: solid;
    border-width: 4px;
    border-radius: 8px;
    padding: 2%;
    margin-top: 10%;
    color: var(--stroke-color);
    position: relative;
    left: 50%;
    transform: translate(-50%, 0);
    height: 30%;
    width: auto;
}

.icon:hover {
    color: var(--stroke-gray-color);
    border-style: solid;
}

.progressBarContainer {
    float: left;
    width: 70%;
    height: 100%;
}

.progressBar {
    position: relative;
    height: 21%;
    width: 100%;
    margin-top: 2%;
    margin-bottom: 2%;
}

.barBackground {
    position: relative;
    float: left;
    height: var(--bar-height);
    width: 76%;
    background-color: var(--stroke-color);
    border-radius: 20px;
    overflow: hidden;
    margin-top: 4px;
    margin-right: 1%;
}

.barProgres {
    height: 100%;
    border-radius: 200px;
    position: relative;
    overflow: hidden;
}
    .barProgres.easy {
        background-color: var(--easy-color);
    }
    .barProgres.hard {
        background-color: var(--hard-color);
    }
    .barProgres.medium {
        background-color: var(--medium-color);
    }
    .barProgres.theory {
        background-color: var(--theory-color);
    }

.barTitle {
    position: relative;
    width: 100%;
    float: left;
}

.barNum {
    position: relative;
    width: 23%;
    float: left;
}

.title {
    position:relative;
    top: 50%;
    transform: translate(0, -50%);
    text-align: center;
}`




const files = [
    {
        path: 'root/index.html',
        language: "html",
        value: indexHTML
    },
    {
        path: 'root/src/App.jsx',
        language: "javascript",
        value: AppJS
    },
    {
        path: 'root/src/App.css',
        language: "css",
        value: AppCSS
    },
    {
        path: 'root/src/Components/Label/Label.jsx',
        language: "javascript",
        value: LabelJS
    },
    {
        path: 'root/src/Components/Label/Label.css',
        language: "css",
        value: LabelCSS
    },
    {
        path: 'root/src/Components/Topics/TopicPanel.jsx',
        language: "javascript",
        value: TopicJS
    },
    {
        path: 'root/src/Components/Topics/TopicPanel.css',
        language: "css",
        value: TopicCSS
    }
]

function makeTree(items) {
    let tree = {}
    for (let item of items) {
        let location = []
        const pathSeperated = item.path.split('/')
        const name = pathSeperated[pathSeperated.length - 1]
        for (let part of pathSeperated) {
            let parent = location.join('/')
            location.push(part)
            let locationString = location.join('/')
            if(!Object.prototype.hasOwnProperty.call(tree, locationString)) {
                tree[locationString] = {data: part, index: locationString, children: []}
                if(part === name) {
                    tree[locationString]['value'] = item.value
                    tree[locationString]['language'] = item.language
                }
                if(parent !== '')
                {
                    tree[parent].children.push(locationString)
                    tree[parent]['isFolder'] = true
                }
            }
        }
    }
    return tree
}

export let tree = makeTree(files)

// export let tree = {
//     root: {
//         data: 'root',
//         index: 'root',
//         children: [ 'root/index.html', 'root/src' ],
//         isFolder: true
//     },
//     'root/index.html': {
//         data: 'index.html',
//         index: 'root/index.html',
//         children: [],
//         value: '<!doctype html>\n' +
//             '<html lang="en">\n' +
//             '  <head>\n' +
//             '    <meta charset="UTF-8" />\n' +
//             '    <link rel="icon" type="image/svg+xml" href="/vite.svg" />\n' +
//             '    <meta name="viewport" content="width=device-width, initial-scale=1.0" />\n' +
//             '    <title>reactapp</title>\n' +
//             '  </head>\n' +
//             '  <body>\n' +
//             '    <div id="root"></div>\n' +
//             '    <script type="module" src="/src/main.jsx"></script>\n' +
//             '  </body>\n' +
//             '</html>\n',
//         language: 'html'
//     },
//     'root/src': {
//         data: 'src',
//         index: 'root/src',
//         children: [ 'root/src/App.jsx', 'root/src/App.css', 'root/src/Components' ],
//         isFolder: true
//     },
//     'root/src/App.jsx': {
//         data: 'App.jsx',
//         index: 'root/src/App.jsx',
//         children: [],
//         value: "import './App.css'\n" +
//             '\n' +
//             'function App() {\n' +
//             '    return <>\n' +
//             '    </>\n' +
//             '}\n' +
//             '\n' +
//             'export default App\n',
//         language: 'javascript'
//     },
//     'root/src/App.css': {
//         data: 'App.css',
//         index: 'root/src/App.css',
//         children: [],
//         value: '.grid {\n' +
//             '    display: grid;\n' +
//             '    grid-template-columns: auto auto auto;\n' +
//             '    width: 0;\n' +
//             '}\n' +
//             '\n' +
//             '.grid > div {\n' +
//             '    margin: 10px;\n' +
//             '}',
//         language: 'css'
//     },
//     'root/src/Components': {
//         data: 'Components',
//         index: 'root/src/Components',
//         children: [ 'root/src/Components/Label', 'root/src/Components/Topics' ],
//         isFolder: true
//     },
//     'root/src/Components/Label': {
//         data: 'Label',
//         index: 'root/src/Components/Label',
//         children: [
//             'root/src/Components/Label/Label.jsx',
//             'root/src/Components/Label/Label.css'
//         ],
//         isFolder: true
//     },
//     'root/src/Components/Label/Label.jsx': {
//         data: 'Label.jsx',
//         index: 'root/src/Components/Label/Label.jsx',
//         children: [],
//         value: 'import styles from "./Label.module.css"\n' +
//             '\n' +
//             'function Label({className, text, size, weight, color}) {\n' +
//             '    return (\n' +
//             '        <>\n' +
//             '            <p className={`${styles.p} \n' +
//             '                           ${styles[size]} \n' +
//             '                           ${styles[weight]} \n' +
//             '                           ${styles[color]} \n' +
//             '                           ${className}`}>\n' +
//             '                {text}\n' +
//             '            </p>\n' +
//             '        </>\n' +
//             '    )\n' +
//             '}\n' +
//             '\n' +
//             'export default Label',
//         language: 'javascript'
//     },
//     'root/src/Components/Label/Label.css': {
//         data: 'Label.css',
//         index: 'root/src/Components/Label/Label.css',
//         children: [],
//         value: '\n' +
//             '.p {\n' +
//             '    font-family: var(--main-font), sans-serif;\n' +
//             '    color: var(--stroke-color);\n' +
//             '    margin: 0;\n' +
//             '}\n' +
//             '\n' +
//             '    .p.mini {\n' +
//             '        font-size: var(--font-mini);\n' +
//             '        height: var(--font-mini);\n' +
//             '    }\n' +
//             '\n' +
//             '    .p.small {\n' +
//             '        font-size: var(--font-small);\n' +
//             '        height: var(--font-small);\n' +
//             '    }\n' +
//             '\n' +
//             '    .p.medium {\n' +
//             '        font-size: var(--font-medium);\n' +
//             '        height: var(--font-medium);\n' +
//             '    }\n' +
//             '\n' +
//             '    .p.large {\n' +
//             '        font-size: var(--font-large);\n' +
//             '        height: var(--font-large);\n' +
//             '    }\n' +
//             '\n' +
//             '    .p.bold {\n' +
//             '        font-weight: bold;\n' +
//             '    }\n' +
//             '\n' +
//             '    .p.stroke {\n' +
//             '        color: var(--stroke-color);\n' +
//             '    }\n' +
//             '\n' +
//             '    .p.strokeGray {\n' +
//             '        color: var(--stroke-gray-color)\n' +
//             '    }',
//         language: 'css'
//     },
//     'root/src/Components/Topics': {
//         data: 'Topics',
//         index: 'root/src/Components/Topics',
//         children: [
//             'root/src/Components/Topics/TopicPanel.jsx',
//             'root/src/Components/Topics/TopicPanel.css'
//         ],
//         isFolder: true
//     },
//     'root/src/Components/Topics/TopicPanel.jsx': {
//         data: 'TopicPanel.jsx',
//         index: 'root/src/Components/Topics/TopicPanel.jsx',
//         children: [],
//         value: 'import styles from "./TopicPanel.module.css"\n' +
//             'import Label from "../Label/Label.jsx";\n' +
//             'import {BookOpenText} from "lucide-react";\n' +
//             'import {NotebookPen} from "lucide-react"\n' +
//             '\n' +
//             'function TopicPanel({topic}) {\n' +
//             '    return (\n' +
//             '        <>\n' +
//             '            <div className={styles.component}>\n' +
//             '                <div className={styles.header}>\n' +
//             '                    <Label className={styles.title} size={"large"} text={topic.name}/>\n' +
//             '                </div>\n' +
//             '                <div className={styles.body}>\n' +
//             '                    <div className={styles.iconsContainer}>\n' +
//             '                        <BookOpenText className={styles.icon}/>\n' +
//             '                        <NotebookPen className={styles.icon}/>\n' +
//             '                    </div>\n' +
//             '                    <div className={styles.progressBarContainer}>\n' +
//             "                        <ProgresBar color={'theory'} completion={topic.theoryCompletion}/>\n" +
//             "                        <ProgresBar color={'easy'} completion={topic.easyCompletion}/>\n" +
//             "                        <ProgresBar color={'medium'} completion={topic.mediumCompletion}/>\n" +
//             "                        <ProgresBar color={'hard'} completion={topic.hardCompletion}/>\n" +
//             '                    </div>\n' +
//             '                </div>\n' +
//             '            </div>\n' +
//             '        </>\n' +
//             '    )\n' +
//             '}\n' +
//             '\n' +
//             'function ProgresBar({color, completion}) {\n' +
//             '\n' +
//             '    const label = color.charAt(0).toUpperCase() + color.slice(1)\n' +
//             "    const [done, all] = completion.split('/')\n" +
//             '    const percentage = 100*done/all\n' +
//             '    return (\n' +
//             '        <>\n' +
//             '\n' +
//             '            <div className={styles.progressBar}>\n' +
//             "                <div className={styles.barTitle}><Label text={label} size={'small'}/></div>\n" +
//             '                <div className={styles.barBackground}>\n' +
//             "                    <div className={`${styles.barProgres} ${styles[color]}`} style={{right: 100-percentage + '%'}}/>\n" +
//             '                </div>\n' +
//             "                <div className={styles.barNum}><Label text={completion} size={'small'}/></div>\n" +
//             '\n' +
//             '            </div>\n' +
//             '\n' +
//             '        </>\n' +
//             '    )\n' +
//             '}\n' +
//             '\n' +
//             'export default TopicPanel',
//         language: 'javascript'
//     },
//     'root/src/Components/Topics/TopicPanel.css': {
//         data: 'TopicPanel.css',
//         index: 'root/src/Components/Topics/TopicPanel.css',
//         children: [],
//         value: ':root {\n' +
//             '    --bar-height: 10px;\n' +
//             '}\n' +
//             '\n' +
//             '.header {\n' +
//             '    background-color: var(--common-color);\n' +
//             '    height: 25%;\n' +
//             '    position: relative;\n' +
//             '    /*z-index: -1;*/\n' +
//             '    border-radius: 17px 17px 0 0;\n' +
//             '    box-shadow: -4px 4px 4px -2px rgb(0,0,0,0.25) inset;\n' +
//             '}\n' +
//             '\n' +
//             '.body {\n' +
//             '    background-color: var(--strong-color);\n' +
//             '    height: 75%;\n' +
//             '    position: relative;\n' +
//             '    /*z-index: -1;*/\n' +
//             '    overflow: hidden;\n' +
//             '    box-shadow: -4px 0 4px -2px rgb(0,0,0,0.25) inset;\n' +
//             '    border-radius: 0 0 17px 17px;\n' +
//             '}\n' +
//             '\n' +
//             '.component {\n' +
//             '    width: 330px;\n' +
//             '    height: 200px;\n' +
//             '    /*box-shadow: -4px 4px 4px rgb(0,0,0,0.25) inset;*/\n' +
//             '    border-radius: 17px;\n' +
//             '    overflow: hidden;\n' +
//             '    border-style: solid;\n' +
//             '    border-color: rgb(0,0,0,0);\n' +
//             '}\n' +
//             '\n' +
//             '.iconsContainer {\n' +
//             '    height: 100%;\n' +
//             '    width: 30%;\n' +
//             '    float: left;\n' +
//             '}\n' +
//             '\n' +
//             '.icon {\n' +
//             '\n' +
//             '    border-style: solid;\n' +
//             '    border-width: 4px;\n' +
//             '    border-radius: 8px;\n' +
//             '    padding: 2%;\n' +
//             '    margin-top: 10%;\n' +
//             '    color: var(--stroke-color);\n' +
//             '    position: relative;\n' +
//             '    left: 50%;\n' +
//             '    transform: translate(-50%, 0);\n' +
//             '    height: 30%;\n' +
//             '    width: auto;\n' +
//             '}\n' +
//             '\n' +
//             '.icon:hover {\n' +
//             '    color: var(--stroke-gray-color);\n' +
//             '    border-style: solid;\n' +
//             '}\n' +
//             '\n' +
//             '.progressBarContainer {\n' +
//             '    float: left;\n' +
//             '    width: 70%;\n' +
//             '    height: 100%;\n' +
//             '}\n' +
//             '\n' +
//             '.progressBar {\n' +
//             '    position: relative;\n' +
//             '    height: 21%;\n' +
//             '    width: 100%;\n' +
//             '    margin-top: 2%;\n' +
//             '    margin-bottom: 2%;\n' +
//             '}\n' +
//             '\n' +
//             '.barBackground {\n' +
//             '    position: relative;\n' +
//             '    float: left;\n' +
//             '    height: var(--bar-height);\n' +
//             '    width: 76%;\n' +
//             '    background-color: var(--stroke-color);\n' +
//             '    border-radius: 20px;\n' +
//             '    overflow: hidden;\n' +
//             '    margin-top: 4px;\n' +
//             '    margin-right: 1%;\n' +
//             '}\n' +
//             '\n' +
//             '.barProgres {\n' +
//             '    height: 100%;\n' +
//             '    border-radius: 200px;\n' +
//             '    position: relative;\n' +
//             '    overflow: hidden;\n' +
//             '}\n' +
//             '    .barProgres.easy {\n' +
//             '        background-color: var(--easy-color);\n' +
//             '    }\n' +
//             '    .barProgres.hard {\n' +
//             '        background-color: var(--hard-color);\n' +
//             '    }\n' +
//             '    .barProgres.medium {\n' +
//             '        background-color: var(--medium-color);\n' +
//             '    }\n' +
//             '    .barProgres.theory {\n' +
//             '        background-color: var(--theory-color);\n' +
//             '    }\n' +
//             '\n' +
//             '.barTitle {\n' +
//             '    position: relative;\n' +
//             '    width: 100%;\n' +
//             '    float: left;\n' +
//             '}\n' +
//             '\n' +
//             '.barNum {\n' +
//             '    position: relative;\n' +
//             '    width: 23%;\n' +
//             '    float: left;\n' +
//             '}\n' +
//             '\n' +
//             '.title {\n' +
//             '    position:relative;\n' +
//             '    top: 50%;\n' +
//             '    transform: translate(0, -50%);\n' +
//             '    text-align: center;\n' +
//             '}',
//         language: 'css'
//     }
// }


console.log(tree)