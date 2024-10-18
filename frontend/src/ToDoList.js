import React, { useState } from "react";
import { useQuery, useMutation, gql } from "@apollo/client";
import { useKeycloak } from "@react-keycloak/web";
import ProfileMenu from "./ProfileMenu";
import UpgradeToPro from "./UpgradeToPro";
import {
  Container,
  TextField,
  Button,
  Typography,
  Card,
  CardContent,
  CardActions,
  Grid,
  Dialog,
  DialogTitle,
  DialogContent,
  Zoom,
} from "@mui/material";

const GET_TODOS = gql`
  query {
    allTodos {
      edges {
        node {
          id
          title
          description
          time
          imageUrl
        }
      }
    }
  }
`;

const CREATE_TODO = gql`
  mutation CreateToDoItem(
    $title: String!
    $description: String
    $imageUrl: String
  ) {
    createTodo(title: $title, description: $description, imageUrl: $imageUrl) {
      todo {
        id
        title
        description
        time
        imageUrl
      }
    }
  }
`;

const UPDATE_TODO = gql`
  mutation UpdateToDoItem(
    $id: ID!
    $title: String
    $description: String
    $imageUrl: String
  ) {
    updateTodo(
      id: $id
      title: $title
      description: $description
      imageUrl: $imageUrl
    ) {
      todo {
        id
        title
        description
        time
        imageUrl
      }
    }
  }
`;

const DELETE_TODO = gql`
  mutation DeleteToDoItem($id: ID!) {
    deleteTodo(id: $id) {
      success
    }
  }
`;

function ToDoList() {
  const { keycloak } = useKeycloak();
  const { loading, error, data, refetch } = useQuery(GET_TODOS);
  const [createTodo] = useMutation(CREATE_TODO);
  const [updateTodo] = useMutation(UPDATE_TODO);
  const [deleteTodo] = useMutation(DELETE_TODO);

  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [image, setImage] = useState(null);
  const [editingId, setEditingId] = useState(null);

  const [open, setOpen] = useState(false);
  const [selectedImage, setSelectedImage] = useState(null);

  const isProUser = keycloak.hasRealmRole("pro_user");

  if (loading) return <p>Loading To-Dos...</p>;
  if (error) return <p>Error loading To-Dos: {error.message}</p>;

  const handleSubmit = async (e) => {
    e.preventDefault();

    let imageUrl = null;

    if (image && isProUser) {
      const formData = new FormData();
      formData.append("image", image);

      const response = await fetch("http://localhost:5000/upload-image", {
        method: "POST",
        headers: {
          Authorization: `Bearer ${keycloak.token}`,
        },
        body: formData,
      });

      const result = await response.json();

      if (response.ok) {
        imageUrl = `http://localhost:5000${result.image_url}`;
      } else {
        console.error(result.message);
        return;
      }
    }

    if (editingId) {
      await updateTodo({
        variables: { id: editingId, title, description, imageUrl },
      });
      setEditingId(null);
    } else {
      await createTodo({
        variables: { title, description, imageUrl },
      });
    }

    setTitle("");
    setDescription("");
    setImage(null);
    refetch();
  };

  const handleEdit = (todo) => {
    setEditingId(todo.id);
    setTitle(todo.title);
    setDescription(todo.description);
  };

  const handleDelete = async (id) => {
    await deleteTodo({
      variables: { id },
    });
    refetch();
  };

  const handleImageClick = (imageUrl) => {
    setSelectedImage(imageUrl);
    setOpen(true);
  };

  const handleClose = () => {
    setOpen(false);
    setSelectedImage(null);
  };

  return (
    <Container maxWidth="md">
      <header
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          margin: "20px 0",
        }}
      >
        <Typography variant="h4">Your To-Do List</Typography>
        <ProfileMenu />
      </header>

      <UpgradeToPro />

      <form onSubmit={handleSubmit} className="mb-4">
        <Grid container spacing={2}>
          <Grid item xs={12}>
            <TextField
              label="Title"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              required
              fullWidth
            />
          </Grid>
          <Grid item xs={12}>
            <TextField
              label="Description"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              multiline
              rows={4}
              fullWidth
            />
          </Grid>
          {isProUser && (
            <Grid item xs={12}>
              <Button variant="contained" component="label">
                Upload Image
                <input
                  type="file"
                  accept="image/*"
                  hidden
                  onChange={(e) => setImage(e.target.files[0])}
                />
              </Button>
              {image && (
                <span style={{ marginLeft: "10px" }}>{image.name}</span>
              )}
            </Grid>
          )}
          <Grid item xs={12}>
            <Button type="submit" variant="contained" color="primary">
              {editingId ? "Update To-Do" : "Add To-Do"}
            </Button>
          </Grid>
        </Grid>
      </form>

      <Grid container spacing={2}>
        {data.allTodos.edges.map(({ node }) => (
          <Grid item xs={12} key={node.id}>
            <Card>
              <CardContent>
                <Typography variant="h5">{node.title}</Typography>
                <Typography variant="body1">{node.description}</Typography>
                {node.imageUrl && (
                  <img
                    src={node.imageUrl}
                    alt="To-Do"
                    style={{
                      maxWidth: "20%",
                      marginTop: "10px",
                      cursor: "pointer",
                    }}
                    onClick={() => handleImageClick(node.imageUrl)}
                  />
                )}

                {/* Display the correct time adjusted for the local timezone */}
                <Typography variant="caption" color="textSecondary">
                  {new Date(node.time).toLocaleString("en-IN", {
                    year: "numeric",
                    month: "short",
                    day: "numeric",
                    hour: "2-digit",
                    minute: "2-digit",
                    second: "2-digit",
                    hour12: false, // Use 24-hour time
                    timeZone: "Asia/Kolkata", // Set the timezone to match your locale
                  })}
                </Typography>
              </CardContent>

              <CardActions>
                <Button
                  onClick={() => handleEdit(node)}
                  variant="contained"
                  color="secondary"
                >
                  Edit
                </Button>
                <Button
                  onClick={() => handleDelete(node.id)}
                  variant="contained"
                  color="error"
                >
                  Delete
                </Button>
              </CardActions>
            </Card>
          </Grid>
        ))}
      </Grid>

      {/* Modal for Image Viewing */}
      <Dialog
        open={open}
        TransitionComponent={Zoom}
        onClose={handleClose}
        maxWidth="lg"
      >
        <DialogTitle>
          <Button onClick={handleClose} variant="contained" color="secondary">
            Close
          </Button>
        </DialogTitle>
        <DialogContent>
          {selectedImage && (
            <img
              src={selectedImage}
              alt="Enlarged To-Do"
              style={{ maxWidth: "100%", maxHeight: "80vh" }}
            />
          )}
        </DialogContent>
      </Dialog>
    </Container>
  );
}

export default ToDoList;
