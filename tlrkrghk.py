        from plotly.colors import n_colors

        base_colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd',
                       '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf']

        for idx, region in enumerate(selected_regions):
            row = df[df["지역"] == region]
            if row.empty:
                continue

            male = row[selected_male_cols].iloc[0].fillna(0).astype(str).str.replace(",", "").astype(float).astype(int)
            female = row[selected_female_cols].iloc[0].fillna(0).astype(str).str.replace(",", "").astype(float).astype(int)

            base_color = base_colors[idx % len(base_colors)]
            # 여성용 연한 색 생성 (opacity 대신 색상 밝게)
            from matplotlib.colors import to_rgba
            import matplotlib.colors as mcolors

            rgba = to_rgba(base_color)
            light_rgba = (rgba[0] + 0.5*(1 - rgba[0]),
                          rgba[1] + 0.5*(1 - rgba[1]),
                          rgba[2] + 0.5*(1 - rgba[2]),
                          1.0)
            light_color = mcolors.to_hex(light_rgba)

            # 남자 막대
            fig.add_trace(go.Bar(
                y=selected_labels,
                x=-male,
                name=f"{region} (남)",
                orientation="h",
                marker_color=base_color,
                legendgroup=region
            ))

            # 여자 막대
            fig.add_trace(go.Bar(
                y=selected_labels,
                x=female,
                name=f"{region} (여)",
                orientation="h",
                marker_color=light_color,
                legendgroup=region
            ))
