import React from "react";
import { shallow } from "zustand/shallow";

import useTasksStore from "../store/useTasksStore";
import Task from "./Task";
import AddTaskForm from "./AddTaskForm";

const Tasks = () => {
  const { tasks, addTask, removeTask } = useTasksStore(
    (store) => store,
    shallow
  );

  return (
    <div>
      <div className="mt-6 mb-12 space-y-6">
        {tasks.map((task) => (
          <Task key={JSON.stringify(task)} onDelete={removeTask} {...task} />
        ))}
      </div>

      <AddTaskForm onSubmit={addTask} />
    </div>
  );
};

export default Tasks;
