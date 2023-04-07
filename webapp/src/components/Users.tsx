import React from "react";
import { useAutoAnimate } from "@formkit/auto-animate/react";
import { shallow } from "zustand/shallow";

import User from "./User";
import useUsersStore from "../store/useUsersStore";

const Users = () => {
  const [usersParent] = useAutoAnimate<HTMLDivElement>();

  const { users, removeUser } = useUsersStore((store) => store, shallow);

  const handleRemoveUser = (username: string) => {
    removeUser(username);
  };

  return (
    <div>
      <div className="space-y-12" ref={usersParent}>
        {users.map(({ username }) => (
          <User
            key={username}
            username={username}
            onDelete={handleRemoveUser}
          />
        ))}
      </div>
    </div>
  );
};

export default Users;
