export function IconComponent({Icon, ...props}) {

    return Icon !== undefined ? <Icon {...props} /> : <></>
}