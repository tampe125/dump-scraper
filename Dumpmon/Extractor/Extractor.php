<?php
/**
 * @package     Dumpmon Scraper
 * @copyright   2015 Davide Tampellini - FabbricaBinaria
 * @license     GNU GPL version 3 or later
 */

namespace Dumpmon\Extractor;

abstract class Extractor
{
    /** @var  string    Data that will be analyzed */
    protected $data;

    /** @var  string    Extracted data from the file */
    protected $extracted;

    /** @var array      Holds all the matcing group after running an extraction */
    protected $matches = array();

    /** @var array      Holds all the regex that will be run on the current text */
    protected $regex = array();

    /**
     * Resets all the internal pointers
     */
    public function reset()
    {
        $this->extracted = '';
        $this->data      = '';
    }

    /**
     * Shorthand method to set all the features to the class
     *
     * @param array $features
     */
    public function setInfo(array $features = array())
    {
        foreach($features as $feature => $value)
        {
            if(property_exists($this, $feature))
            {
                $this->$feature = $value;
            }
        }
    }

    public function getExtractedData()
    {
        return trim($this->extracted);
    }

    /**
     * Entry point for analyzing the file
     *
     * @return void
     */
    public abstract function analyze();

    protected function extractData($regex)
    {
        $this->matches = array();

        $this->data = preg_replace_callback($regex, array($this, 'replaceMatches'), $this->data);

        return implode("\n", $this->matches);
    }

    /**
     * This function should be used as callback function while extracting data.
     * In this way we can fetch the info and replace it with dummy text, avoiding double extractions
     *
     * @param $matches
     *
     * @return string
     */
    protected function replaceMatches($matches)
    {
        if(isset($matches[1]))
        {
            $this->matches[] = trim($matches[1]);
        }

        return '';
    }
}