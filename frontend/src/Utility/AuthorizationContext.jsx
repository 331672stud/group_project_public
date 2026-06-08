import {createContext} from "react";

export const AuthorizationContext = createContext({user: null, setUser: null});