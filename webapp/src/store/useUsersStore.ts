import { create } from "zustand";
import { immer } from "zustand/middleware/immer";

export type Task = {
  job: string;
  weight: number;
  deadline: number;
};

export type User = {
  username: string;
  tasks: Task[];
};

interface InitialState {
  users: User[];
}

interface UseUsersStore extends InitialState {
  addUser: (username: string) => void;
  removeUser: (username: string) => void;
  addTask: (username: string, task: Task) => void;
  removeTask: (username: string, task: Task) => void;
}

const initialState: InitialState = {
  users: [],
};

const useUsersStore = create(
  immer<UseUsersStore>((set) => ({
    ...initialState,

    addTask(username, task) {
      set((store) => {
        const userIndex = store.users.findIndex(
          (user) => user.username === username
        );

        const duplicateTask = store.users[userIndex].tasks.find(
          (t) => t.job === task.job
        );

        if (duplicateTask) return;

        store.users[userIndex].tasks.push(task);
      });
    },

    removeTask(username, task) {
      set((store) => {
        const userIndex = store.users.findIndex(
          (user) => user.username === username
        );

        store.users[userIndex].tasks = store.users[userIndex].tasks.filter(
          (t) => t.job !== task.job
        );
      });
    },

    addUser(username) {
      set((store) => {
        store.users.unshift({
          username,
          tasks: [],
        });
      });
    },

    removeUser(username) {
      set((store) => {
        store.users = store.users.filter((user) => user.username !== username);
      });
    },
  }))
);

export default useUsersStore;
