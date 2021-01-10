import React from "react";
import { render, cleanup } from "@testing-library/react";

import UsersList from "../UsersList";

afterEach(cleanup);

const users = [
  {
    email: "musa6ali@gmail.com",
    id: 1,
    username: "musa",
  },
  {
    email: "musa@mali.org",
    id: 2,
    username: "musaali",
  },
];

it("renders a username", () => {
  const { getByText } = render(<UsersList users={users} />);
  expect(getByText("musa")).toHaveClass("username");
  expect(getByText("musaali")).toHaveClass("username");
});

it("renders", () => {
  const { asFragment } = render(<UsersList users={users} />);
  expect(asFragment()).toMatchSnapshot();
});
