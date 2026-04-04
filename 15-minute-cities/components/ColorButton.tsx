"use client";

import { getColorPalette } from "@/utils/scoreColor";
import { Box, Card, CardContent, Stack, Typography } from "@mui/material";
import Button from "@mui/material/Button";

type ColorButtonProps = {
	colorBlindMode: boolean;
	onToggle: () => void;
};

export default function ColorButton({ colorBlindMode, onToggle }: ColorButtonProps) {
	const legend = getColorPalette(colorBlindMode).map((color, index) => {
		const label = ["Very low", "Low", "Medium", "High"][index];
		return { color, label };
	});

	return (
		<div
			style={{
				position: "absolute",
				top: 16,
				right: 16,
				zIndex: 10,
			}}
		>
			<Card
				sx={{
					width: 200,
					height: 220,
				}}
			>
				<CardContent>
					<Typography variant="h6" gutterBottom>Legend</Typography>
					<Stack spacing={1}>
						{legend.map((item, index) => (
							<Box key={index} sx={{ display: "flex", alignItems: "center" }}>
								<Box
									sx={{
										width: 20,
										height: 20,
										backgroundColor: item.color,
										border: "1px solid #ccc",
										marginRight: 1,
									}}
								/>
								<Typography variant="body2">{item.label}</Typography>
							</Box>
						))}
					</Stack>
					<Box sx={{ height: 16 }} />
					<Button
						variant="contained"
						onClick={onToggle}
						sx={{
							backgroundColor: "#000000",
							color: "#ffffff",
							"&:hover": {
								backgroundColor: "#292727",
							},
						}}
					>
						{colorBlindMode ? "Color blind: on" : "Color blind: off"}
					</Button>
				</CardContent>
			</Card>
		</div>
	);
}
