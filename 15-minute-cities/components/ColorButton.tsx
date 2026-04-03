"use client";

import Button from "@mui/material/Button";

type ColorButtonProps = {
	colorBlindMode: boolean;
	onToggle: () => void;
};

export default function ColorButton({ colorBlindMode, onToggle }: ColorButtonProps) {
	return (
		<div
			style={{
				position: "absolute",
				top: 16,
				right: 16,
				zIndex: 10,
			}}
		>
			<Button
				variant="contained"
				onClick={onToggle}
				sx={{
					backgroundColor: "#000000",
					color: "#fffff",
					"&:hover": {
						backgroundColor: "#292727",
					},
				}}
			>
				{colorBlindMode ? "Color blind: on" : "Color blind: off"}
			</Button>
		</div>
	);
}
