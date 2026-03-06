with col_data:
    st.markdown("### 📊 לוח נתונים (Live)")
    
    h2h_html = "".join([f"<div style='font-size: 0.85rem; padding: 6px 0; border-bottom: 1px solid rgba(255,255,255,0.05); color:#e8f4f8;'>{m}</div>" for m in deep_data["h2h_matches"]])
    if not h2h_html: h2h_html = "<span style='color:gray;'>אין מפגשים קודמים קרובים.</span>"
    
    st.markdown(f"""
        <div class='data-box'>
            <h4>יחסי זכייה (Odds)</h4>
            <b>1:</b> {deep_data['odds'].get('1', '-')} &nbsp;|&nbsp; 
            <b>X:</b> {deep_data['odds'].get('X', '-')} &nbsp;|&nbsp; 
            <b>2:</b> {deep_data['odds'].get('2', '-')}
        </div>
        
        <div class='data-box'>
            <h4>כושר נוכחי (5 משחקים אחרונים)</h4>
            <div style='display:flex; justify-content:space-between; margin-bottom:12px; background:rgba(0,0,0,0.2); padding:10px; border-radius:6px;'>
                <div style='text-align:right;'>
                    <div style='font-size:0.75rem; color:gray; margin-bottom:4px;'>{selected_game['home']} (כללי)</div>
                    {render_form_badges(deep_data['home_form'])}
                </div>
                <div style='text-align:left;'>
                    <div style='font-size:0.75rem; color:gray; margin-bottom:4px;'>{selected_game['away']} (כללי)</div>
                    {render_form_badges(deep_data['away_form'])}
                </div>
            </div>
            <div style='display:flex; justify-content:space-between; padding:0 10px;'>
                <div style='text-align:right;'>
                    <div style='font-size:0.75rem; color:#00f0ff; margin-bottom:4px;'>{selected_game['home']} (בבית)</div>
                    {render_form_badges(deep_data['home_home_form'])}
                </div>
                <div style='text-align:left;'>
                    <div style='font-size:0.75rem; color:#00f0ff; margin-bottom:4px;'>{selected_game['away']} (בחוץ)</div>
                    {render_form_badges(deep_data['away_away_form'])}
                </div>
            </div>
        </div>

        <div class='data-box'>
            <h4>⚔️ היסטוריית מפגשים (H2H - אחרונים)</h4>
            {h2h_html}
        </div>
        
        <div class='data-box'>
            <h4>🚑 פצועים / הרכבים חסרים</h4>
            <div style='display:flex; justify-content:space-between; gap: 15px;'>
                <div style='text-align:right; flex:1;'>
                    <div style='font-size:0.75rem; color:#00f0ff; margin-bottom:4px; font-weight:bold;'>{selected_game['home']}</div>
                    <span style='color:#ff3b5c; font-size:0.8rem; line-height:1.4;'>{deep_data['missing_home']}</span>
                </div>
                <div style='text-align:left; flex:1;'>
                    <div style='font-size:0.75rem; color:#00f0ff; margin-bottom:4px; font-weight:bold;'>{selected_game['away']}</div>
                    <span style='color:#ff3b5c; font-size:0.8rem; line-height:1.4;'>{deep_data['missing_away']}</span>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)
