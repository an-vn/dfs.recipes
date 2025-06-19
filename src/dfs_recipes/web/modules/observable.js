class Observable {
    constructor() {
        this.observers = [];
    }

    subscribe(func) {
        this.observers.push(func);
    }

    unsubscribe(func) {
        this.observers = this.observers.filter((observer) => observer !== func);
    }

    notify(data) {
        this.observers.forEach((observer) => observer.handleNotify(data));
    }
}

class Observer {
    constructor(name) {
        this.name = name;
    }

    handleNotify(data) {
        console.log(`${this.name} received update: ${data}`);
    }
}

export {
    Observable
}
