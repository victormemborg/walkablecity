"use client";

import Button from "@mui/material/Button";

type ColorButtonProps = {
	colorBlindMode: boolean;
	onToggle: () => void;
};

export default function ColorButton({ colorBlindMode, onToggle }: ColorButtonProps) {
  return (
    <Button
      variant="contained"
      onClick={onToggle}
      fullWidth
      sx={{
        backgroundColor: "#000000",
        color: "#ffffff",
        fontSize: "0.8rem",
        fontWeight: 700,
        letterSpacing: "0.02em",
        "&:hover": {
          backgroundColor: "#292727",
        },
      }}
    >
      {colorBlindMode ? "Color blind mode: on" : "Color blind mode: off"}
    </Button>
  );
}
