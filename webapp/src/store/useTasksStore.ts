import { create } from "zustand";
import { immer } from "zustand/middleware/immer";
import { persist } from "zustand/middleware";

import { Task } from "./useUsersStore";

export type TaskType = "all" | "specified";

interface InitialState {
  tasks: Task[];
  all: TaskType;
}

interface UseTasksStore extends InitialState {
  addTask: (task: Task) => void;
  removeTask: (task: Task) => void;
  setAll: (all: TaskType) => void;
}

const initialState: InitialState = {
  tasks: [],
  all: "specified",
};

const useTasksStore = create(
  persist(
    immer<UseTasksStore>((set) => ({
      ...initialState,

      setAll(all) {
        set((store) => {
          store.all = all;
        });
      },

      addTask(task) {
        set((store) => {
          const duplicateTask = store.tasks.find((t) => t.job === task.job);

          if (duplicateTask) return;

          store.tasks.push(task);
        });
      },

      removeTask(task) {
        set((store) => {
          store.tasks = store.tasks.filter((t) => t.job !== task.job);
        });
      },
    })),
    {
      name: "jarvis-tasks",
    }
  )
);

export default useTasksStore;
