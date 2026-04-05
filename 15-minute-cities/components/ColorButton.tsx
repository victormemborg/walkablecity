"use client";

import { buildLegend } from "@/utils/legend";
import type { ScoreRange } from "@/types/mapTypes";
import { Box, Card, CardContent, Stack, Typography } from "@mui/material";
import Button from "@mui/material/Button";

type ColorButtonProps = {
	colorBlindMode: boolean;
  currentRange: ScoreRange | null;
	onToggle: () => void;
};

export default function ColorButton({ colorBlindMode, currentRange, onToggle }: ColorButtonProps) {
  const legend = currentRange ? buildLegend(currentRange, colorBlindMode) :[];

  return (
    <div style={{ position: "absolute", top: 16, right: 16, zIndex: 10 }}>
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
          <Box sx={{ height: 12 }} />
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
        </CardContent>
      </Card>
    </div>
  );
}
