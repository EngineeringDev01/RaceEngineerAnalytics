import plotly.graph_objects as go


class TelemetryPlotter:


    def __init__(self, dataframe):

        self.data = dataframe


    def speed_throttle_brake(self):

        fig = go.Figure()


        # Speed
        fig.add_trace(
            go.Scatter(
                x=self.data["Distance"],
                y=self.data["Wheel Speed FL"],
                name="Speed FL",
                mode="lines"
            )
        )


        # Throttle
        fig.add_trace(
            go.Scatter(
                x=self.data["Distance"],
                y=self.data["Throttle Pos"],
                name="Throttle %",
                mode="lines",
                yaxis="y2"
            )
        )


        # Brake
        fig.add_trace(
            go.Scatter(
                x=self.data["Distance"],
                y=self.data["Brk_Press_Fnt"],
                name="Front Brake Pressure",
                mode="lines",
                yaxis="y2"
            )
        )


        fig.update_layout(

            title="Speed / Throttle / Brake vs Distance",

            xaxis=dict(
                title="Distance [m]"
            ),

            yaxis=dict(
                title="Speed [km/h]"
            ),

            yaxis2=dict(

                title="Driver Inputs [% / bar]",

                overlaying="y",

                side="right"

            ),

            hovermode="x unified",

            height=700

        )


        return fig