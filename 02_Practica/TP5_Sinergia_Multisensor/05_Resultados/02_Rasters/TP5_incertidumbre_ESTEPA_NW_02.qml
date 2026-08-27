<!DOCTYPE qgis><qgis version="3.34" styleCategories="Symbology">
  <!-- Incertidumbre de la biomasa (Mg/ha), cadena completa
       ADVERTENCIA: el modelo de altura subestima los arboles altos (sesgo medido
       de casi 10 m por encima de 15 m) y la alometria lo amplifica. Este mapa
       SUBESTIMA los rodales altos. Ver TP5_03 y TP5_04. -->
  <pipe><rasterrenderer type="singlebandpseudocolor" band="1" opacity="1">
    <rastershader><colorrampshader classificationMode="1" colorRampType="INTERPOLATED">
      <item value="0" color="#ffffff" label="0"/>
      <item value="15" color="#cccccc" label="15"/>
      <item value="40" color="#525252" label="40"/>
    </colorrampshader></rastershader>
  </rasterrenderer></pipe>
</qgis>
