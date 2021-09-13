const redux=require('redux');
const createStore = redux.createStore;
const combineReducers=redux.combineReducers;
const applyMiddleware=redux.applyMiddleware();

const Buy_Book="Buy_Book";

const initialStateBook={
    noOfBooks :10,
 };

const initialStatePen={
     noOfPens :15
};

function BuyBook() {
    return {
        type:Buy_Book,
        payload:"my first rudex",
    };
}

function BuyPen() {
    return {
        type:"Buy_Pen",
        payload:"my first rudex",
    };
}

const reducerBook=(state=initialStateBook,action)=>{
    switch (action.type) {
        case ("Buy_Book"):
        return{
            ...initialStateBook,noOfBooks:state.noOfBooks-1
        };
        default:return initialStateBook;
    }
};


const reducerPen=(state=initialStatePen,action)=>{
    switch (action.type) {
        case ("Buy_Pen"):
            return {
                ...initialStatePen,noOfPens: state.noOfPens-1
            };
        default:return initialStatePen;
    }
};

const reducer=combineReducers({
    Book:reducerBook,
    pen:reducerPen
});
const store=createStore(reducer);
console.log("initial state",store.getState());
const Unsubscribe = store.subscribe(()=>{console.log('updated state value',store.getState())});
store.dispatch(BuyBook());
store.dispatch(BuyBook());
store.dispatch(BuyBook());
store.dispatch(BuyPen());
store.dispatch(BuyPen());
store.dispatch(BuyPen());
Unsubscribe();



