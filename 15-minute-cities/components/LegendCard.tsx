"use client";

import type { ScoreRange } from "@/types/mapTypes";
import { buildLegend } from "@/utils/legend";
import { Box, Card, CardContent, Stack, Typography } from "@mui/material";

type LegendCardProps = {
	colorBlindMode: boolean;
	currentRange: ScoreRange | null;
};

export default function LegendCard({ colorBlindMode, currentRange }: LegendCardProps) {
	const legend = currentRange ? buildLegend(currentRange, colorBlindMode) : [];

	return (
		<Card sx={{ width: 220 }}>
			<CardContent sx={{ p: 2 }}>
				<Typography variant="h6" sx={{ fontWeight: 600 }} gutterBottom>
					Legend
				</Typography>
				<Stack spacing={1}>
					{currentRange ? (
						legend.map((item, index) => (
							<Box key={index} sx={{ display: "flex", alignItems: "center" }}>
								<Box
									sx={{
										width: 20,
										height: 20,
										backgroundColor: item.color,
										border: "1px solid #bdbdbd",
										mr: 1,
									}}
								/>
								<Typography variant="body2">{item.label}</Typography>
							</Box>
						))
					) : (
						<Typography variant="body2" color="text.secondary">
							Loading score range...
						</Typography>
					)}
				</Stack>
			</CardContent>
		</Card>
	);
}
