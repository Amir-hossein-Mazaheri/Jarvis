import { create } from "zustand";
import { immer } from "zustand/middleware/immer";
import { persist } from "zustand/middleware";

export type Task = {
  job: string;
  weight: number;
  deadline: number;
};

export type User = {
  nickname: string;
  username: string;
  tasks: Task[];
};

interface InitialState {
  users: User[];
}

interface UseUsersStore extends InitialState {
  addUser: (username: string, nickname: string) => void;
  removeUser: (username: string) => void;
  addTask: (username: string, task: Task) => void;
  removeTask: (username: string, task: Task) => void;
  clearTasks: (username: string) => void;
  clearUsers: () => void;
}

const initialState: InitialState = {
  users: [],
};

const useUsersStore = create(
  persist(
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

      addUser(username, nickname) {
        set((store) => {
          const duplicateUser = store.users.find(
            (u) => u.username === username
          );

          if (duplicateUser) return;

          store.users.unshift({
            nickname,
            username,
            tasks: [],
          });
        });
      },

      removeUser(username) {
        set((store) => {
          store.users = store.users.filter(
            (user) => user.username !== username
          );
        });
      },

      clearTasks(username) {
        set((store) => {
          const userIndex = store.users.findIndex(
            (user) => user.username === username
          );

          store.users[userIndex].tasks = [];
        });
      },

      clearUsers() {
        set((store) => {
          store.users = [];
        });
      },
    })),
    {
      name: "jarvis-users",
    }
  )
);

export default useUsersStore;
